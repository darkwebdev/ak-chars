"""Main server entry - mounts auth and players routers and logs HTTP traffic."""

import time
import logging
import json
import re
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from strawberry.fastapi import GraphQLRouter

from .auth import router as auth_router
from .players import router as players_router
from .fixtures import router as fixtures_router
from .graphql_schema import schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ak-chars.server')

app = FastAPI(title='ak-chars-auth')

# Configure CORS
import os
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5193",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5193",
]
# Add production origin if CORS_ORIGIN env var is set
if os.getenv("CORS_ORIGIN"):
    allowed_origins.append(os.getenv("CORS_ORIGIN"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sanitize_sensitive_data(text: str) -> str:
    """Mask sensitive data in logs to prevent credential leakage."""
    try:
        data = json.loads(text)
        sensitive_fields = {
            'yostar_token', 'token', 'channel_uid', 'channelUid',
            'password', 'secret', 'api_key', 'apiKey',
            'code', 'authorization', 'auth', 'email'
        }
        
        def mask_dict(obj):
            if isinstance(obj, dict):
                return {
                    k: '***REDACTED***' if k.lower() in {f.lower() for f in sensitive_fields}
                    else mask_dict(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [mask_dict(item) for item in obj]
            return obj
        
        masked = mask_dict(data)
        return json.dumps(masked)
    except Exception:
        patterns = [
            (r'"(yostar_token|token|channel_uid|channelUid|password|secret|api_key|apiKey|code|authorization|email)"\s*:\s*"[^"]*"', r'"\1": "***REDACTED***"'),
            (r"'(yostar_token|token|channel_uid|channelUid|password|secret|api_key|apiKey|code|authorization|email)'\s*:\s*'[^']*'", r"'\1': '***REDACTED***'"),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


def sanitize_headers(headers: dict) -> dict:
    """Remove sensitive headers from logs."""
    safe_headers = {}
    sensitive_keys = {'authorization', 'cookie', 'x-api-key', 'api-key'}
    for key, value in headers.items():
        if key.lower() in sensitive_keys:
            safe_headers[key] = '***REDACTED***'
        else:
            safe_headers[key] = value
    return safe_headers


@app.middleware('http')
async def log_requests(request: Request, call_next: Callable):
    start = time.time()
    try:
        req_body_bytes = await request.body()
        try:
            req_body = req_body_bytes.decode('utf-8')
        except Exception:
            req_body = repr(req_body_bytes)[:1000]
    except Exception as e:
        req_body = f'<could not read body: {e}>'

    safe_headers = sanitize_headers(dict(request.headers))
    safe_body = sanitize_sensitive_data(req_body[:2000])
    logger.info('--> %s %s headers=%s body=%s', request.method, request.url.path, safe_headers, safe_body)

    response = await call_next(request)

    try:
        if isinstance(response, StreamingResponse):
            body = b''
            async for chunk in response.body_iterator:
                body += chunk
            text = body.decode('utf-8', errors='replace')
            safe_resp_body = sanitize_sensitive_data(text[:2000])
            new_response = Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
            duration = time.time() - start
            logger.info('<-- %s %s status=%s time=%.3fs body=%s', request.method, request.url.path, response.status_code, duration, safe_resp_body)
            return new_response
        else:
            try:
                resp_body = response.body
            except Exception:
                resp_body = b''
            if isinstance(resp_body, (bytes, bytearray)):
                text = resp_body.decode('utf-8', errors='replace')
            else:
                text = str(resp_body)
            safe_resp_body = sanitize_sensitive_data(text[:2000])
            duration = time.time() - start
            logger.info('<-- %s %s status=%s time=%.3fs body=%s', request.method, request.url.path, response.status_code, duration, safe_resp_body)
            return response
    except Exception as e:
        logger.exception('Error logging response: %s', e)
        return response


# Mount API routers
app.include_router(auth_router)
app.include_router(players_router)
app.include_router(fixtures_router)

# Mount GraphQL endpoint with CORS support
graphql_app = GraphQLRouter(
    schema,
    graphiql=True,
)
app.include_router(graphql_app, prefix="/graphql")
