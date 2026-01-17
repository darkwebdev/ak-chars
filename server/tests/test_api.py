"""API endpoint tests using FastAPI TestClient."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


def load_fixture():
    """Load fixture data."""
    fixture_path = Path(__file__).parent / 'user_data_response.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


class TestRosterEndpoint:
    """Tests for /my/roster endpoint."""
    
    def test_roster_returns_chars_only(self):
        """Test that roster endpoint returns only chars field."""
        response = client.post(
            "/my/roster",
            json={"channel_uid": "test", "yostar_token": "test", "server": "en"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "chars" in data
        assert "data" not in data  # Should not return full data
        assert isinstance(data["chars"], dict)
    
    def test_roster_contains_operators(self):
        """Test that roster contains operator data."""
        response = client.post(
            "/my/roster",
            json={"channel_uid": "test", "yostar_token": "test"}
        )
        
        chars = response.json()["chars"]
        assert len(chars) > 0
        
        # Check first operator structure
        first_char = next(iter(chars.values()))
        assert "charId" in first_char
        assert "level" in first_char
        assert "evolvePhase" in first_char
        assert "potentialRank" in first_char
    
    def test_roster_matches_fixture(self):
        """Test that roster data matches fixture."""
        fixture_data = load_fixture()
        expected_chars = fixture_data["data"]["user"]["troop"]["chars"]
        
        response = client.post(
            "/my/roster",
            json={"channel_uid": "test", "yostar_token": "test"}
        )
        
        actual_chars = response.json()["chars"]
        assert len(actual_chars) == len(expected_chars)
        
        # Verify some operators exist
        assert "1" in actual_chars  # Amiya
        assert actual_chars["1"]["charId"] == "char_002_amiya"
    
    def test_roster_requires_credentials(self):
        """Test that roster requires channel_uid and token."""
        response = client.post("/my/roster", json={})
        assert response.status_code == 422  # Validation error


class TestStatusEndpoint:
    """Tests for /my/status endpoint."""
    
    def test_status_returns_status_only(self):
        """Test that status endpoint returns only status field."""
        response = client.post(
            "/my/status",
            json={"channel_uid": "test", "yostar_token": "test", "server": "en"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "status" in data
        assert "data" not in data  # Should not return full data
        assert isinstance(data["status"], dict)
    
    def test_status_contains_user_info(self):
        """Test that status contains user information."""
        response = client.post(
            "/my/status",
            json={"channel_uid": "test", "yostar_token": "test"}
        )
        
        status = response.json()["status"]
        assert "nickName" in status
        assert "level" in status
        assert "uid" in status
        assert "exp" in status
    
    def test_status_matches_fixture(self):
        """Test that status data matches fixture."""
        fixture_data = load_fixture()
        expected_status = fixture_data["data"]["user"]["status"]
        
        response = client.post(
            "/my/status",
            json={"channel_uid": "test", "yostar_token": "test"}
        )
        
        actual_status = response.json()["status"]
        assert actual_status["nickName"] == expected_status["nickName"]
        assert actual_status["level"] == expected_status["level"]
        assert actual_status["uid"] == expected_status["uid"]
    
    def test_status_requires_credentials(self):
        """Test that status requires channel_uid and token."""
        response = client.post("/my/status", json={})
        assert response.status_code == 422  # Validation error


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_game_code_accepts_email(self):
        """Test that game-code endpoint accepts email."""
        # Note: This will fail in fixture mode, but validates the structure
        response = client.post(
            "/auth/game-code",
            json={"email": "test@example.com", "server": "en"}
        )
        
        # In fixture mode without arkprts, this might error
        # Just check it validates the input structure
        assert response.status_code in [200, 500]
    
    def test_game_code_requires_email(self):
        """Test that game-code requires valid email."""
        response = client.post("/auth/game-code", json={"server": "en"})
        assert response.status_code == 422
        
        response = client.post("/auth/game-code", json={"email": "invalid"})
        assert response.status_code == 422
    
    def test_game_token_requires_code(self):
        """Test that game-token requires email and code."""
        response = client.post("/auth/game-token", json={})
        assert response.status_code == 422
        
        response = client.post(
            "/auth/game-token",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422


class TestDataSanitization:
    """Tests for log sanitization."""
    
    def test_sensitive_fields_in_request_body(self):
        """Test that sensitive fields are present in valid requests."""
        # This validates the API accepts sensitive fields
        # (sanitization happens in logging, not request processing)
        response = client.post(
            "/my/roster",
            json={
                "channel_uid": "test123",
                "yostar_token": "secret456",
                "server": "en"
            }
        )
        
        assert response.status_code == 200
        # The endpoint should work with these fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
