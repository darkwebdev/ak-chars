"""Tests for credential caching functionality."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from tests.integration.credential_cache import (
    save_credentials,
    load_credentials,
    clear_cache,
    CACHE_FILE,
    CACHE_DURATION
)


@pytest.fixture
def test_credentials():
    """Sample credentials for testing."""
    return {
        "channel_uid": "test_channel_123",
        "yostar_token": "test_token_abc"
    }


@pytest.fixture
def test_email():
    """Test email address."""
    return "test@example.com"


@pytest.fixture
def test_server():
    """Test server."""
    return "en"


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up cache file before and after each test."""
    clear_cache()
    yield
    clear_cache()


class TestSaveCredentials:
    """Tests for saving credentials to cache."""

    def test_save_creates_cache_file(self, test_credentials, test_email, test_server):
        """Test that save_credentials creates the cache file."""
        save_credentials(test_credentials, test_email, test_server)
        assert CACHE_FILE.exists()

    def test_save_creates_valid_json(self, test_credentials, test_email, test_server):
        """Test that saved cache is valid JSON."""
        save_credentials(test_credentials, test_email, test_server)

        with open(CACHE_FILE) as f:
            data = json.load(f)

        assert isinstance(data, dict)

    def test_save_includes_all_fields(self, test_credentials, test_email, test_server):
        """Test that saved cache includes all required fields."""
        save_credentials(test_credentials, test_email, test_server)

        with open(CACHE_FILE) as f:
            data = json.load(f)

        assert "credentials" in data
        assert "email" in data
        assert "server" in data
        assert "timestamp" in data

    def test_save_stores_correct_credentials(self, test_credentials, test_email, test_server):
        """Test that credentials are stored correctly."""
        save_credentials(test_credentials, test_email, test_server)

        with open(CACHE_FILE) as f:
            data = json.load(f)

        assert data["credentials"]["channel_uid"] == test_credentials["channel_uid"]
        assert data["credentials"]["yostar_token"] == test_credentials["yostar_token"]

    def test_save_stores_correct_metadata(self, test_credentials, test_email, test_server):
        """Test that email and server are stored correctly."""
        save_credentials(test_credentials, test_email, test_server)

        with open(CACHE_FILE) as f:
            data = json.load(f)

        assert data["email"] == test_email
        assert data["server"] == test_server

    def test_save_creates_valid_timestamp(self, test_credentials, test_email, test_server):
        """Test that timestamp is valid and recent."""
        before = datetime.now()
        save_credentials(test_credentials, test_email, test_server)
        after = datetime.now()

        with open(CACHE_FILE) as f:
            data = json.load(f)

        timestamp = datetime.fromisoformat(data["timestamp"])
        assert before <= timestamp <= after


class TestLoadCredentials:
    """Tests for loading credentials from cache."""

    def test_load_returns_none_when_file_missing(self, test_email, test_server):
        """Test that load returns None when cache file doesn't exist."""
        result = load_credentials(test_email, test_server)
        assert result is None

    def test_load_returns_credentials_when_valid(self, test_credentials, test_email, test_server):
        """Test that load returns credentials when cache is valid."""
        save_credentials(test_credentials, test_email, test_server)

        result = load_credentials(test_email, test_server)

        assert result is not None
        assert result["channel_uid"] == test_credentials["channel_uid"]
        assert result["yostar_token"] == test_credentials["yostar_token"]

    def test_load_returns_none_when_email_mismatch(self, test_credentials, test_email, test_server):
        """Test that load returns None when email doesn't match."""
        save_credentials(test_credentials, test_email, test_server)

        result = load_credentials("different@example.com", test_server)

        assert result is None

    def test_load_returns_none_when_server_mismatch(self, test_credentials, test_email, test_server):
        """Test that load returns None when server doesn't match."""
        save_credentials(test_credentials, test_email, test_server)

        result = load_credentials(test_email, "jp")

        assert result is None

    def test_load_returns_none_when_expired(self, test_credentials, test_email, test_server):
        """Test that load returns None when cache is expired."""
        # Save credentials
        save_credentials(test_credentials, test_email, test_server)

        # Manually modify timestamp to be expired (> CACHE_DURATION ago)
        with open(CACHE_FILE) as f:
            data = json.load(f)

        old_timestamp = datetime.now() - CACHE_DURATION - timedelta(hours=1)
        data["timestamp"] = old_timestamp.isoformat()

        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

        result = load_credentials(test_email, test_server)

        assert result is None

    def test_load_handles_malformed_json(self, test_email, test_server):
        """Test that load handles malformed JSON gracefully."""
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            f.write("{ invalid json }")

        result = load_credentials(test_email, test_server)

        assert result is None

    def test_load_handles_missing_fields(self, test_email, test_server):
        """Test that load handles missing required fields."""
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump({"incomplete": "data"}, f)

        result = load_credentials(test_email, test_server)

        assert result is None

    def test_load_validates_timestamp_within_duration(self, test_credentials, test_email, test_server):
        """Test that credentials within cache duration are loaded."""
        # Save credentials
        save_credentials(test_credentials, test_email, test_server)

        # Modify timestamp to be just before expiry
        with open(CACHE_FILE) as f:
            data = json.load(f)

        almost_expired = datetime.now() - CACHE_DURATION + timedelta(minutes=5)
        data["timestamp"] = almost_expired.isoformat()

        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

        result = load_credentials(test_email, test_server)

        assert result is not None
        assert result["channel_uid"] == test_credentials["channel_uid"]


class TestClearCache:
    """Tests for clearing the cache."""

    def test_clear_removes_cache_file(self, test_credentials, test_email, test_server):
        """Test that clear_cache removes the cache file."""
        save_credentials(test_credentials, test_email, test_server)
        assert CACHE_FILE.exists()

        clear_cache()

        assert not CACHE_FILE.exists()

    def test_clear_does_not_error_when_file_missing(self):
        """Test that clear_cache doesn't error when file doesn't exist."""
        clear_cache()  # Should not raise an exception


class TestCachePersistence:
    """Integration tests for cache persistence across save/load cycles."""

    def test_save_and_load_roundtrip(self, test_credentials, test_email, test_server):
        """Test that credentials survive save/load roundtrip."""
        save_credentials(test_credentials, test_email, test_server)
        loaded = load_credentials(test_email, test_server)

        assert loaded == test_credentials

    def test_multiple_save_overwrites(self, test_email, test_server):
        """Test that saving multiple times overwrites previous data."""
        credentials1 = {"channel_uid": "uid1", "yostar_token": "token1"}
        credentials2 = {"channel_uid": "uid2", "yostar_token": "token2"}

        save_credentials(credentials1, test_email, test_server)
        save_credentials(credentials2, test_email, test_server)

        loaded = load_credentials(test_email, test_server)

        assert loaded == credentials2

    def test_cache_file_location(self):
        """Test that cache file is in expected location."""
        expected_path = Path(__file__).parent / ".credentials_cache.json"
        assert CACHE_FILE == expected_path


class TestCacheDuration:
    """Tests for cache duration configuration."""

    def test_cache_duration_is_configured(self):
        """Test that CACHE_DURATION is properly configured."""
        assert isinstance(CACHE_DURATION, timedelta)
        assert CACHE_DURATION.total_seconds() > 0

    def test_cache_respects_duration_setting(self, test_credentials, test_email, test_server):
        """Test that cache expiration respects CACHE_DURATION setting."""
        save_credentials(test_credentials, test_email, test_server)

        # Modify timestamp to exactly CACHE_DURATION ago
        with open(CACHE_FILE) as f:
            data = json.load(f)

        exact_expiry = datetime.now() - CACHE_DURATION
        data["timestamp"] = exact_expiry.isoformat()

        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

        result = load_credentials(test_email, test_server)

        # Should be expired (> CACHE_DURATION)
        assert result is None


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_empty_credentials_dict(self, test_email, test_server):
        """Test handling of empty credentials dictionary."""
        empty_creds = {}
        save_credentials(empty_creds, test_email, test_server)

        loaded = load_credentials(test_email, test_server)

        assert loaded == empty_creds

    def test_special_characters_in_email(self, test_credentials, test_server):
        """Test handling of special characters in email."""
        special_email = "test+filter@example.com"
        save_credentials(test_credentials, special_email, test_server)

        loaded = load_credentials(special_email, test_server)

        assert loaded == test_credentials

    def test_different_servers(self, test_credentials, test_email):
        """Test that different servers maintain separate caches."""
        save_credentials(test_credentials, test_email, "en")

        # Try loading with different server
        loaded_en = load_credentials(test_email, "en")
        loaded_jp = load_credentials(test_email, "jp")

        assert loaded_en == test_credentials
        assert loaded_jp is None

    def test_case_sensitive_email(self, test_credentials, test_server):
        """Test that email comparison is case-sensitive."""
        email_lower = "test@example.com"
        email_upper = "TEST@EXAMPLE.COM"

        save_credentials(test_credentials, email_lower, test_server)

        loaded_lower = load_credentials(email_lower, test_server)
        loaded_upper = load_credentials(email_upper, test_server)

        assert loaded_lower == test_credentials
        assert loaded_upper is None  # Case doesn't match

    def test_large_credentials(self, test_email, test_server):
        """Test handling of large credential values."""
        large_creds = {
            "channel_uid": "x" * 1000,
            "yostar_token": "y" * 1000
        }

        save_credentials(large_creds, test_email, test_server)
        loaded = load_credentials(test_email, test_server)

        assert loaded == large_creds
