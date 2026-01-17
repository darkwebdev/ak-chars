from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional

from .ark_client import expand_player_ids, search_players, _make_client

router = APIRouter()


class IdsPayload(BaseModel):
    ids: List[str]
    server: Optional[str] = 'en'


class SearchPayload(BaseModel):
    nickname: str
    server: Optional[str] = 'en'
    limit: Optional[int] = 10


@router.post('/players/expand')
async def players_expand(payload: IdsPayload):
    try:
        out = await expand_player_ids(payload.ids, server=payload.server)
        return {'ok': True, 'players': out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/players/search')
async def players_search(payload: SearchPayload):
    try:
        out = await search_players(payload.nickname, server=payload.server, limit=payload.limit)
        return {'ok': True, 'players': out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/characters/{player_id}')
async def character_detail(player_id: str, server: Optional[str] = 'en'):
    """Return an expanded player summary for a single player id.

    This uses the same expand path as `/players/expand` but is convenient for
    quick lookups from the frontend or curl.
    """
    try:
        out = await expand_player_ids([player_id], server=server)
        if not out:
            raise HTTPException(status_code=404, detail='player not found')
        return {'ok': True, 'player': out[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/avatars/{player_id}')
async def avatar_proxy(player_id: str, server: Optional[str] = 'en'):
    """Proxy an avatar image for the requested player id.

    This attempts to use the arkprts client to fetch an avatar URL or raw
    bytes and returns it with the correct content-type. If the arkprts client
    is unavailable or doesn't provide an avatar, a 404 is returned.
    """
    try:
        client = _make_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f'ark client unavailable: {e}')

    # First, try to fetch raw player info which often contains avatar/asset ids
    try:
        if hasattr(client, 'get_raw_player_info'):
            raw = await client.get_raw_player_info([player_id], server=server)
            # raw may be a dict with 'players' list
            players = None
            if isinstance(raw, dict) and 'players' in raw:
                players = raw['players']
            elif isinstance(raw, list):
                players = raw

            if players:
                p = players[0]
                # common avatar fields in raw data
                avatar = p.get('avatar') if isinstance(p, dict) else None
                avatar_id = None
                if isinstance(avatar, dict):
                    avatar_id = avatar.get('id') or avatar.get('avatarId')
                if not avatar_id:
                    avatar_id = p.get('avatarId') or p.get('avatar')

                # try to resolve asset via client.assets
                assets = getattr(client, 'assets', None)
                if assets and avatar_id:
                    # try get_file then get_item
                    for fn in ('get_file', 'get_item', 'get_module'):
                        if hasattr(assets, fn):
                            try:
                                resolver = getattr(assets, fn)
                                maybe = resolver(avatar_id)
                                if hasattr(maybe, '__await__'):
                                    maybe = await maybe
                                # if bytes or filepath
                                if isinstance(maybe, (bytes, bytearray)):
                                    return Response(content=maybe, media_type='image/png')
                                # if resolver returned a path-like or dict with url
                                if isinstance(maybe, str) and maybe.startswith('http'):
                                    import httpx

                                    r = httpx.get(maybe, timeout=10.0)
                                    if r.status_code == 200:
                                        return Response(content=r.content, media_type=r.headers.get('content-type', 'image/png'))
                                if isinstance(maybe, dict):
                                    # try common keys
                                    url = maybe.get('url') or maybe.get('path')
                                    if url and isinstance(url, str) and url.startswith('http'):
                                        import httpx

                                        r = httpx.get(url, timeout=10.0)
                                        if r.status_code == 200:
                                            return Response(content=r.content, media_type=r.headers.get('content-type', 'image/png'))
                            except Exception:
                                continue

    except Exception:
        # don't fail hard on avatar discovery; fall through to other methods
        pass

    # Try to use common API names to fetch avatar bytes or url
    for fn_name in ('get_player_avatar_bytes', 'get_avatar', 'avatar', 'player_avatar'):
        if hasattr(client, fn_name):
            fn = getattr(client, fn_name)
            try:
                maybe = fn(player_id, server=server)
                if hasattr(maybe, '__await__'):
                    maybe = await maybe
                # maybe is bytes or (bytes, content_type) or URL
                if isinstance(maybe, bytes):
                    return Response(content=maybe, media_type='image/png')
                if isinstance(maybe, tuple) and len(maybe) == 2 and isinstance(maybe[0], (bytes, bytearray)):
                    content_type = maybe[1] or 'application/octet-stream'
                    return Response(content=maybe[0], media_type=content_type)
                if isinstance(maybe, str) and maybe.startswith('http'):
                    # simple proxying: fetch the url on the server and return bytes
                    import httpx

                    r = httpx.get(maybe, timeout=10.0)
                    if r.status_code == 200:
                        return Response(content=r.content, media_type=r.headers.get('content-type', 'image/png'))
            except Exception:
                continue

    # If no client method matched or we couldn't fetch, return 404
    raise HTTPException(status_code=404, detail='avatar not available')


@router.get('/players/raw/{player_id}')
async def player_raw(player_id: str, server: Optional[str] = 'en'):
    """Return the full raw upstream JSON payload for a single player id.

    This is useful for debugging and for UIs that need the complete data
    (avatars, full roster, stats)."""
    try:
        client = _make_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f'ark client unavailable: {e}')

    if not hasattr(client, 'get_raw_player_info'):
        raise HTTPException(status_code=501, detail='ark client does not support get_raw_player_info')

    try:
        raw = await client.get_raw_player_info([player_id], server=server)
        return {'ok': True, 'raw': raw}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RawIdsPayload(BaseModel):
    ids: List[str]
    server: Optional[str] = 'en'


@router.post('/players/raw')
async def players_raw(payload: RawIdsPayload):
    """Return raw upstream JSON payloads for multiple player ids."""
    try:
        client = _make_client()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f'ark client unavailable: {e}')

    if not hasattr(client, 'get_raw_player_info'):
        raise HTTPException(status_code=501, detail='ark client does not support get_raw_player_info')

    try:
        raw = await client.get_raw_player_info(payload.ids, server=payload.server)
        return {'ok': True, 'raw': raw}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
