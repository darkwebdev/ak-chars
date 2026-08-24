"""Final arkprts client helpers used by the server.

This module exposes a small, stable API used by the FastAPI server. It
constructs arkprts.Client with assets=False to avoid large asset
downloads. Functions raise RuntimeError when arkprts or expected client
APIs are missing so errors are visible during development.
"""

from typing import List, Dict
import json
import logging

try:
    import arkprts
except Exception:
    arkprts = None


def generate_device_id() -> str:
    """Generate a fresh device identity, JSON-encoded as an opaque string.

    Callers are expected to persist this alongside channel_uid/yostar_token
    and pass it back on every subsequent authenticated call (see
    get_user_data's device_id param) - without this, every call generates
    its own random device identity and presents as a brand-new device to
    Yostar on every request, which we have reason to believe is what
    triggers Yostar kicking a user's live game session on each fetch.
    """
    from arkprts.auth import create_random_device_ids
    return json.dumps(create_random_device_ids())


def _apply_device_id(auth, device_id) -> None:
    """Override an Auth instance's randomly-generated device_ids with a
    persisted one, if a valid one was supplied. Silently falls back to
    the auto-generated random ids on any malformed input, rather than
    failing the whole auth flow over a bad/stale persisted value."""
    if not device_id:
        return
    try:
        ids = json.loads(device_id)
        if isinstance(ids, list) and len(ids) == 3 and all(isinstance(i, str) for i in ids):
            auth.device_ids = tuple(ids)
    except (TypeError, ValueError):
        pass


def _require_client_class():
    if not arkprts:
        raise RuntimeError('arkprts package not installed')
    Client = getattr(arkprts, 'Client', None)
    if Client is None:
        raise RuntimeError('arkprts.Client not found')
    return Client


def _make_client():
    Client = _require_client_class()
    return Client(assets=False)


async def get_characters(game_username: str) -> List[Dict]:
    """Return compact player summaries for a username.

    Each summary contains at least 'id' and 'name'.
    """
    Client = _require_client_class()
    client = Client(assets=False)

    # prefer the documented search API when available
    if hasattr(client, 'search_players'):
        players = await client.search_players(game_username, server='en')
        return [
            {
                'id': getattr(p, 'uid', None) or getattr(p, 'id', None) or getattr(p, 'player_id', None) or str(p),
                'name': getattr(p, 'nickname', None) or getattr(p, 'nick', None) or getattr(p, 'name', None) or str(p),
            }
            for p in players
        ]

    # fallback: attempt a generic players lookup
    if hasattr(client, 'get_players'):
        players = await client.get_players([game_username], server='en')
        return [
            {
                'id': getattr(p, 'uid', None) or getattr(p, 'id', None) or getattr(p, 'player_id', None) or str(p),
                'name': getattr(p, 'nickname', None) or getattr(p, 'nick', None) or getattr(p, 'name', None) or str(p),
            }
            for p in players
        ]

    # no known API available
    raise RuntimeError('arkprts client does not expose a known player lookup API')
async def expand_player_ids(ids: list[str], server: str = 'en') -> list[dict]:
    """Given a list of player ids, return compact player summaries.

    Each summary is a dict with keys: id, name, level (if available).
    """
    logger = logging.getLogger('ak-chars.ark_client')
    client = _make_client()
    out: list[dict] = []

    # Try bulk lookup first if available
    if hasattr(client, 'get_players'):
        try:
            players = await client.get_players(ids, server=server)
            for p in players:
                pid = getattr(p, 'uid', None) or getattr(p, 'id', None) or getattr(p, 'player_id', None) or str(p)
                name = getattr(p, 'nickname', None) or getattr(p, 'nick', None) or getattr(p, 'name', None) or str(p)
                level = getattr(p, 'level', None)
                out.append({'id': str(pid), 'name': name, 'level': level})
        except Exception as e:
            logger.debug('bulk get_players failed: %s', e)

    # Per-id fallbacks for clients that don't support bulk or returned partial results
    for pid_in in ids:
        if any(p.get('id') == str(pid_in) for p in out):
            continue

        found = None

        # try common single-player methods
        for fn_name in ('get_player', 'get_player_by_id', 'get_player_by_uid', 'get_character', 'fetch_player'):
            if hasattr(client, fn_name):
                try:
                    fn = getattr(client, fn_name)
                    maybe = fn(pid_in, server=server)
                    if hasattr(maybe, '__await__'):
                        maybe = await maybe
                    if maybe:
                        found = maybe
                        break
                except Exception:
                    continue

        # fallback to search by id (some APIs allow searching by uid or nickname)
        if not found and hasattr(client, 'search_players'):
            try:
                res = await client.search_players(str(pid_in), server=server, limit=1)
                if res:
                    found = res[0]
            except Exception:
                pass

        if found:
            p = found
            pid = getattr(p, 'uid', None) or getattr(p, 'id', None) or getattr(p, 'player_id', None) or str(p)
            name = getattr(p, 'nickname', None) or getattr(p, 'nick', None) or getattr(p, 'name', None) or str(p)
            level = getattr(p, 'level', None)
            out.append({'id': str(pid), 'name': name, 'level': level})

    return out


async def search_players(nickname: str, server: str = 'en', limit: int | None = 10) -> list[dict]:
    """Search for players by nickname and return compact summaries."""
    client = _make_client()
    players = await client.search_players(nickname, server=server, limit=limit)
    out = []
    for p in players:
        pid = getattr(p, 'uid', None) or getattr(p, 'id', None) or getattr(p, 'player_id', None) or str(p)
        name = getattr(p, 'nickname', None) or getattr(p, 'nick', None) or getattr(p, 'name', None) or str(p)
        level = getattr(p, 'level', None)
        out.append({'id': pid, 'name': name, 'level': level})
    return out


async def send_game_auth_code(email: str, server: str = 'en') -> bool:
    """Send authentication code to email via Yostar.

    Returns True if code was sent successfully.
    """
    if not arkprts:
        raise RuntimeError('arkprts package not installed')

    YostarAuth = getattr(arkprts, 'YostarAuth', None)
    if YostarAuth is None:
        raise RuntimeError('arkprts.YostarAuth not found - authentication not supported')

    # Create auth instance for the server
    auth = YostarAuth(server)
    await auth.send_email_code(email)
    return True


async def get_game_token_from_code(email: str, code: str, server: str = 'en') -> tuple[str, str, str]:
    """Get Yostar authentication token using email and code.

    Returns tuple of (channel_uid, yostar_token, device_id). device_id is a
    freshly generated device identity (see generate_device_id) that the
    caller should persist and pass back to get_user_data on every
    subsequent call, to avoid presenting as a new device each time.
    """
    if not arkprts:
        raise RuntimeError('arkprts package not installed')

    YostarAuth = getattr(arkprts, 'YostarAuth', None)
    if YostarAuth is None:
        raise RuntimeError('arkprts.YostarAuth not found - authentication not supported')

    # Create auth instance and get token
    auth = YostarAuth(server)
    channel_uid, token = await auth.get_token_from_email_code(email=email, code=code)
    return channel_uid, token, generate_device_id()


async def get_user_data(channel_uid: str, yostar_token: str, server: str = 'en', device_id: str = None) -> dict:
    """Get authenticated user's full game data including complete operator roster.

    Requires game credentials (channelUid and yostar token). If device_id
    (from get_game_token_from_code) is supplied, reuses that persisted
    device identity instead of generating a new random one for this call -
    see generate_device_id's docstring for why that matters.
    Returns raw game data with all operators, inventory, and account info.
    """
    Client = _require_client_class()

    # Check if YostarAuth is available
    YostarAuth = getattr(arkprts, 'YostarAuth', None)
    if YostarAuth is None:
        raise RuntimeError('arkprts.YostarAuth not found - authentication not supported')

    # Build the authenticated client manually rather than via the
    # from_token() convenience wrapper, so we can override the randomly
    # generated device_ids with a persisted one first.
    auth = YostarAuth(server=server)
    _apply_device_id(auth, device_id)
    await auth.login_with_token(channel_uid, yostar_token)
    client = Client(auth=auth, server=server, assets=False)
    
    # Get full user data
    if hasattr(client, 'get_raw_data'):
        return await client.get_raw_data()
    elif hasattr(client, 'get_data'):
        data = await client.get_data()
        # Convert model to dict if needed
        if hasattr(data, 'dict'):
            return data.dict()
        elif hasattr(data, '__dict__'):
            return data.__dict__
        return data
    else:
        raise RuntimeError('arkprts client does not expose get_data or get_raw_data')
