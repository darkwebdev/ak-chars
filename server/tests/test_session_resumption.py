"""Tests for persisted-session support (server/ark_client.py's
_session_to_json/_parse_session, and get_user_data's session-resumption
branch), the alternative to device-id persistence after live testing
confirmed device_id alone does not stop Yostar from kicking the user's
live game session (see generate_device_id's docstring).

get_user_data now returns a (data, session) tuple, and myRoster/myStatus/
myInventory (both REST and GraphQL) surface the updated session via the
X-Ak-Session response header so callers can resume without a fresh login
on their next call.
"""
import sys
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.ark_client import _session_to_json, _parse_session

client = TestClient(app)


class TestParseSession:
    def test_parses_valid_session(self):
        raw = json.dumps({'uid': 'u1', 'secret': 's1', 'seqnum': 5})
        assert _parse_session(raw) == {'uid': 'u1', 'secret': 's1', 'seqnum': 5}

    def test_returns_none_for_none(self):
        assert _parse_session(None) is None

    def test_returns_none_for_empty_string(self):
        assert _parse_session('') is None

    def test_returns_none_for_malformed_json(self):
        assert _parse_session('not valid json') is None

    def test_returns_none_when_missing_required_keys(self):
        assert _parse_session(json.dumps({'uid': 'u1'})) is None

    def test_returns_none_for_non_dict_json(self):
        assert _parse_session(json.dumps(['uid', 'secret', 'seqnum'])) is None


class TestSessionToJson:
    def test_serializes_auth_session(self):
        auth = MagicMock()
        auth.session.uid = 'u1'
        auth.session.secret = 's1'
        auth.session.seqnum = 3
        assert json.loads(_session_to_json(auth)) == {'uid': 'u1', 'secret': 's1', 'seqnum': 3}


class TestGetUserDataUsesSessionResumption:
    """Confirm a valid `session` skips login_with_token entirely in favor of
    YostarAuth.from_session, and a missing/invalid one falls back to login."""

    @patch('server.ark_client.arkprts')
    @pytest.mark.asyncio
    async def test_resumes_session_when_valid(self, mock_arkprts):
        from server.ark_client import get_user_data

        mock_auth = MagicMock()
        mock_auth.session.uid = 'u1'
        mock_auth.session.secret = 's1'
        mock_auth.session.seqnum = 2
        mock_arkprts.YostarAuth.from_session = AsyncMock(return_value=mock_auth)

        mock_client = MagicMock()
        mock_client.get_raw_data = AsyncMock(return_value={'user': {}})
        mock_arkprts.Client.return_value = mock_client

        session_in = json.dumps({'uid': 'u1', 'secret': 's1', 'seqnum': 1})
        data, session_out = await get_user_data('x', 'y', 'en', None, session_in)

        mock_arkprts.YostarAuth.from_session.assert_awaited_once()
        mock_auth.login_with_token.assert_not_called()
        assert json.loads(session_out) == {'uid': 'u1', 'secret': 's1', 'seqnum': 2}

    @patch('server.ark_client.arkprts')
    @pytest.mark.asyncio
    async def test_falls_back_to_login_when_no_session(self, mock_arkprts):
        from server.ark_client import get_user_data

        mock_auth = MagicMock()
        mock_auth.login_with_token = AsyncMock()
        mock_auth.session.uid = 'u1'
        mock_auth.session.secret = 's1'
        mock_auth.session.seqnum = 1
        mock_arkprts.YostarAuth.return_value = mock_auth

        mock_client = MagicMock()
        mock_client.get_raw_data = AsyncMock(return_value={'user': {}})
        mock_arkprts.Client.return_value = mock_client

        data, session_out = await get_user_data('x', 'y', 'en', None, None)

        mock_auth.login_with_token.assert_awaited_once_with('x', 'y')
        assert json.loads(session_out) == {'uid': 'u1', 'secret': 's1', 'seqnum': 1}


class TestXAkSessionHeader:
    """The REST /my/status and /my/roster endpoints must surface the
    returned session via the X-Ak-Session response header."""

    @patch('server.auth.USE_FIXTURES', False)
    @patch('server.auth.get_user_data', new_callable=AsyncMock)
    def test_my_status_sets_session_header(self, mock_get_user_data):
        mock_get_user_data.return_value = (
            {'user': {'status': {'nickName': 'Test', 'nickNumber': '0000', 'level': 1,
                                  'exp': 0, 'socialPoint': 0, 'uid': '1'}}},
            '{"uid": "1", "secret": "s", "seqnum": 7}',
        )

        response = client.post('/my/status', json={'channel_uid': 'x', 'yostar_token': 'y'})
        assert response.status_code == 200
        assert response.headers['x-ak-session'] == '{"uid": "1", "secret": "s", "seqnum": 7}'

    @patch('server.auth.USE_FIXTURES', False)
    @patch('server.auth.get_user_data', new_callable=AsyncMock)
    def test_my_roster_sets_session_header(self, mock_get_user_data):
        mock_get_user_data.return_value = (
            {'user': {'troop': {'chars': {}}}},
            '{"uid": "1", "secret": "s", "seqnum": 8}',
        )

        response = client.post('/my/roster', json={'channel_uid': 'x', 'yostar_token': 'y'})
        assert response.status_code == 200
        assert response.headers['x-ak-session'] == '{"uid": "1", "secret": "s", "seqnum": 8}'

    @patch('server.graphql_schema.USE_FIXTURES', False)
    @patch('server.ark_client.get_user_data', new_callable=AsyncMock)
    def test_graphql_my_inventory_sets_session_header(self, mock_get_user_data):
        mock_get_user_data.return_value = (
            {'user': {'status': {'diamondShard': 10, 'payDiamond': 1, 'freeDiamond': 2, 'gachaTicket': 3}}},
            '{"uid": "1", "secret": "s", "seqnum": 9}',
        )

        query = """
        {
          myInventory(channelUid: "x", yostarToken: "y") {
            orundum
          }
        }
        """
        response = client.post('/graphql', json={'query': query})
        assert response.status_code == 200
        assert response.json()['data']['myInventory']['orundum'] == 10
        assert response.headers['x-ak-session'] == '{"uid": "1", "secret": "s", "seqnum": 9}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
