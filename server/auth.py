from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os
import json
from pathlib import Path
from dotenv import load_dotenv

import logging
from .ark_client import get_user_data, send_game_auth_code, get_game_token_from_code

logger = logging.getLogger('ak-chars.auth')

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

router = APIRouter()

USE_FIXTURES = os.getenv('USE_FIXTURES', 'true').lower() == 'true'


def load_fixture_data():
    """Load user data from fixture file for development."""
    fixture_path = Path(__file__).parent / 'tests' / 'user_data_response.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


class MyRosterRequest(BaseModel):
    channel_uid: str
    yostar_token: str
    server: str = 'en'


class MyStatusRequest(BaseModel):
    channel_uid: str
    yostar_token: str
    server: str = 'en'


class GameCodeRequest(BaseModel):
    email: EmailStr
    server: str = 'en'


class GameTokenRequest(BaseModel):
    email: EmailStr
    code: str
    server: str = 'en'


@router.post('/my/roster')
async def my_roster(req: MyRosterRequest):
    """Get the authenticated user's operator roster.
    
    Returns only user.troop.chars - the complete operator roster with stats.
    
    In development mode (USE_FIXTURES=true), returns fixture data.
    In production, requires game credentials to authenticate with the game API.
    """
    try:
        if USE_FIXTURES:
            fixture_data = load_fixture_data()
            chars = fixture_data.get('data', {}).get('user', {}).get('troop', {}).get('chars', {})
            logger.info('Returning fixture roster data (%d operators)', len(chars))
            return {'ok': True, 'chars': chars}
        
        data = await get_user_data(req.channel_uid, req.yostar_token, req.server)
        chars = data.get('user', {}).get('troop', {}).get('chars', {})
        logger.info('Fetched roster for server=%s (%d operators)', req.server, len(chars))
        return {'ok': True, 'chars': chars}
    except Exception as e:
        logger.exception('Error fetching roster: %s', e)
        raise HTTPException(status_code=500, detail=f'Error fetching roster: {e}')


@router.post('/my/status')
async def my_status(req: MyStatusRequest):
    """Get the authenticated user's status information.
    
    Returns only user.status - player status including level, AP, nickName, etc.
    
    In development mode (USE_FIXTURES=true), returns fixture data.
    In production, requires game credentials to authenticate with the game API.
    """
    try:
        if USE_FIXTURES:
            fixture_data = load_fixture_data()
            status = fixture_data.get('data', {}).get('user', {}).get('status', {})
            logger.info('Returning fixture status data')
            return {'ok': True, 'status': status}
        
        data = await get_user_data(req.channel_uid, req.yostar_token, req.server)
        status = data.get('user', {}).get('status', {})
        logger.info('Fetched user status for server=%s', req.server)
        return {'ok': True, 'status': status}
    except Exception as e:
        logger.exception('Error fetching user status: %s', e)
        raise HTTPException(status_code=500, detail=f'Error fetching user status: {e}')


@router.post('/auth/game-code')
async def game_code(payload: GameCodeRequest):
    """Request a game authentication code from Yostar.

    Sends a verification code to the email address associated with your game account.
    Use this code with /auth/game-token to get your game credentials.
    """
    try:
        await send_game_auth_code(payload.email, payload.server)
        logger.info('Sent game auth code for server %s', payload.server)
        return {'ok': True, 'message': 'Code sent to email'}
    except Exception as e:
        logger.exception('Error sending game auth code: %s', e)
        # Preserve error structure from arkprts for better error handling
        error_str = str(e)
        # Try to parse arkprts error JSON
        import json
        try:
            error_data = json.loads(error_str)
            # Return structured error with code
            raise HTTPException(
                status_code=500,
                detail={
                    'error': 'Error sending code',
                    'code': error_data.get('Code'),
                    'message': error_data.get('Msg'),
                    'raw': error_str
                }
            )
        except (json.JSONDecodeError, ValueError):
            # Fallback to generic error
            raise HTTPException(status_code=500, detail=f'Error sending code: {e}')


@router.post('/auth/game-token')
async def game_token(payload: GameTokenRequest):
    """Get game authentication token using email and code.
    
    After receiving a code via /auth/game-code, use this endpoint to get
    your channel_uid and yostar_token. These credentials can be used with
    /my/roster to get your full operator roster.
    
    SECURITY NOTE: This endpoint returns sensitive authentication credentials.
    Store these securely client-side and never log or expose them.
    """
    try:
        channel_uid, token = await get_game_token_from_code(payload.email, payload.code, payload.server)
        logger.info('Generated game token for server %s', payload.server)
        return {
            'ok': True,
            'channel_uid': channel_uid,
            'yostar_token': token,
            'server': payload.server
        }
    except Exception as e:
        logger.exception('Error getting game token: %s', e)
        raise HTTPException(status_code=400, detail=f'Error getting token: {e}')
