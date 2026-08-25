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

    NOTE: tested live and confirmed this alone does NOT stop Yostar from
    kicking the user's live game session on every fetch - kept because
    it's harmless and still used for the very first login (before any
    session exists to resume, see get_user_data's session param below),
    but session resumption is the mechanism actually expected to help.
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


def _session_to_json(auth) -> str:
    """Serialize an Auth's live session (uid/secret/seqnum) to an opaque
    string, to be persisted by the caller and passed to a later call's
    `session` param via _resume_session, so that call can skip the login
    handshake entirely instead of just varying its device identity."""
    s = auth.session
    return json.dumps({'uid': s.uid, 'secret': s.secret, 'seqnum': s.seqnum})


def _parse_session(session: str):
    """Parse a persisted session string back into a dict, or None if
    missing/malformed (falls back to a fresh login in that case)."""
    if not session:
        return None
    try:
        data = json.loads(session)
        if isinstance(data, dict) and {'uid', 'secret', 'seqnum'} <= data.keys():
            return data
    except (TypeError, ValueError):
        pass
    return None


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


async def get_user_data(channel_uid: str, yostar_token: str, server: str = 'en', device_id: str = None, session: str = None) -> tuple:
    """Get authenticated user's full game data including complete operator roster.

    Requires game credentials (channelUid and yostar token).

    If `session` (from a previous call's returned session, see below) is
    valid, resumes that session via YostarAuth.from_session() instead of
    logging in at all - login itself, not device identity, is suspected to
    be what makes Yostar kick the user's live game session (device_id
    alone was tried and confirmed not to help - see generate_device_id's
    docstring). Falls back to a fresh login (using device_id if supplied)
    when no valid session is given, e.g. on the first call after
    obtaining channel_uid/yostar_token.

    Returns a (data, session) tuple. `session` is the JSON-encoded, opaque
    live session (uid/secret/seqnum) after this call - the seqnum
    increments on every authenticated request, so callers must persist
    and pass back the returned value, not the one they sent in, or the
    *next* call will use a stale seqnum.
    """
    Client = _require_client_class()

    # Check if YostarAuth is available
    YostarAuth = getattr(arkprts, 'YostarAuth', None)
    if YostarAuth is None:
        raise RuntimeError('arkprts.YostarAuth not found - authentication not supported')

    parsed_session = _parse_session(session)
    if parsed_session is not None:
        network = arkprts.NetworkSession(default_server=server)
        auth = await YostarAuth.from_session(
            server=server,
            uid=parsed_session['uid'],
            secret=parsed_session['secret'],
            seqnum=parsed_session['seqnum'],
            network=network,
        )
    else:
        # Build the authenticated client manually rather than via the
        # from_token() convenience wrapper, so we can override the
        # randomly generated device_ids with a persisted one first.
        auth = YostarAuth(server=server)
        _apply_device_id(auth, device_id)
        await auth.login_with_token(channel_uid, yostar_token)

    client = Client(auth=auth, server=server, assets=False)

    # Get full user data
    if hasattr(client, 'get_raw_data'):
        data = await client.get_raw_data()
    elif hasattr(client, 'get_data'):
        raw = await client.get_data()
        # Convert model to dict if needed
        if hasattr(raw, 'dict'):
            data = raw.dict()
        elif hasattr(raw, '__dict__'):
            data = raw.__dict__
        else:
            data = raw
    else:
        raise RuntimeError('arkprts client does not expose get_data or get_raw_data')

    return data, _session_to_json(auth)
