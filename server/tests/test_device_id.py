"""Tests for persisted-device-identity support (server/ark_client.py's
generate_device_id/_apply_device_id, and the deviceId plumbing through
getAuthToken -> myRoster/myStatus/myInventory).

Context: every authenticated call previously constructed a fresh, random
device identity and sent it to Yostar on every request (via
YostarAuth.from_token -> Auth.__init__ -> create_random_device_ids()).
If Yostar enforces one active session per device, that would explain why
a live game session got kicked on every fetch. getAuthToken now returns
a deviceId the client is expected to persist and pass back on every
subsequent call, so the same device identity is reused instead of a new
one being generated each time.
"""
import sys
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient
from server.main import app
from server.ark_client import generate_device_id, _apply_device_id

client = TestClient(app)


class TestGenerateDeviceId:
    def test_returns_json_encoded_triple(self):
        device_id = generate_device_id()
        ids = json.loads(device_id)
        assert isinstance(ids, list)
        assert len(ids) == 3
        assert all(isinstance(i, str) for i in ids)

    def test_generates_different_ids_each_time(self):
        assert generate_device_id() != generate_device_id()


class TestApplyDeviceId:
    class FakeAuth:
        def __init__(self):
            self.device_ids = ("random1", "random2", "random3")

    def test_overrides_with_valid_device_id(self):
        auth = self.FakeAuth()
        _apply_device_id(auth, json.dumps(["a", "b", "c"]))
        assert auth.device_ids == ("a", "b", "c")

    def test_leaves_unchanged_when_device_id_is_none(self):
        auth = self.FakeAuth()
        original = auth.device_ids
        _apply_device_id(auth, None)
        assert auth.device_ids == original

    def test_leaves_unchanged_on_malformed_json(self):
        auth = self.FakeAuth()
        original = auth.device_ids
        _apply_device_id(auth, "not valid json")
        assert auth.device_ids == original

    def test_leaves_unchanged_on_wrong_shape(self):
        auth = self.FakeAuth()
        original = auth.device_ids
        _apply_device_id(auth, json.dumps(["only", "two"]))
        assert auth.device_ids == original


class TestGetAuthTokenReturnsDeviceId:
    @patch('server.ark_client.get_game_token_from_code')
    @pytest.mark.asyncio
    async def test_get_auth_token_includes_device_id(self, mock_get_token):
        mock_get_token.return_value = ('mock_channel_uid', 'mock_yostar_token', json.dumps(["d1", "d2", "d3"]))

        query = """
        mutation {
          getAuthToken(email: "test@example.com", code: "123456") {
            success
            channelUid
            yostarToken
            deviceId
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        result = response.json()["data"]["getAuthToken"]
        assert result["success"] is True
        assert result["deviceId"] == json.dumps(["d1", "d2", "d3"])


class TestDeviceIdReachesUpstreamCall:
    """Confirm deviceId actually flows from the GraphQL argument through to
    the ark_client.get_user_data call, not just accepted and dropped."""

    @patch('server.graphql_schema.USE_FIXTURES', False)
    @patch('server.ark_client.get_user_data', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_my_status_passes_device_id_through(self, mock_get_user_data):
        mock_get_user_data.return_value = {
            'user': {
                'status': {
                    'nickName': 'Test', 'nickNumber': '0000', 'level': 1,
                    'exp': 0, 'socialPoint': 0, 'uid': '1',
                }
            }
        }

        query = """
        {
          myStatus(channelUid: "x", yostarToken: "y", deviceId: "[\\"d1\\",\\"d2\\",\\"d3\\"]") {
            uid
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        assert response.json()["data"]["myStatus"]["uid"] == "1"

        mock_get_user_data.assert_awaited_once_with("x", "y", "en", '["d1","d2","d3"]')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
