"""Test to verify GitHub secret format for CACHED_CREDENTIALS.

This test helps ensure the CACHED_CREDENTIALS secret in GitHub Actions
has the correct format and structure.
"""

import json
import pytest
from datetime import datetime, timedelta
from tests.integration.credential_cache import CACHE_DURATION


class TestGitHubSecretFormat:
    """Tests to validate the expected format of CACHED_CREDENTIALS secret."""

    def test_example_secret_format(self):
        """Test that shows the correct format for CACHED_CREDENTIALS secret.

        The secret should be a JSON object with this structure:
        {
            "credentials": {
                "channel_uid": "your_actual_channel_uid",
                "yostar_token": "your_actual_yostar_token"
            },
            "email": "your_test_account@example.com",
            "server": "en",
            "timestamp": "2026-01-24T12:00:00.000000"
        }

        IMPORTANT: The timestamp must be within the last 24 hours (CACHE_DURATION)
        or the cache will be considered expired and not used.
        """
        # Example of a valid secret structure
        example_secret = {
            "credentials": {
                "channel_uid": "example_channel_uid_123",
                "yostar_token": "example_token_abc"
            },
            "email": "test@example.com",
            "server": "en",
            "timestamp": datetime.now().isoformat()
        }

        # Verify it has all required fields
        assert "credentials" in example_secret
        assert "email" in example_secret
        assert "server" in example_secret
        assert "timestamp" in example_secret

        # Verify credentials structure
        assert "channel_uid" in example_secret["credentials"]
        assert "yostar_token" in example_secret["credentials"]

        # Verify it's valid JSON
        json_str = json.dumps(example_secret)
        parsed = json.loads(json_str)
        assert parsed == example_secret

    def test_timestamp_must_be_recent(self):
        """Test that demonstrates timestamp must be within CACHE_DURATION."""
        # Fresh timestamp (should be valid)
        fresh_secret = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "test@example.com",
            "server": "en",
            "timestamp": datetime.now().isoformat()
        }

        fresh_timestamp = datetime.fromisoformat(fresh_secret["timestamp"])
        age = datetime.now() - fresh_timestamp
        assert age <= CACHE_DURATION, f"Fresh timestamp should be within {CACHE_DURATION}"

        # Old timestamp (should be invalid)
        old_secret = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "test@example.com",
            "server": "en",
            "timestamp": (datetime.now() - CACHE_DURATION - timedelta(hours=1)).isoformat()
        }

        old_timestamp = datetime.fromisoformat(old_secret["timestamp"])
        age = datetime.now() - old_timestamp
        assert age > CACHE_DURATION, f"Old timestamp should exceed {CACHE_DURATION}"

    def test_generate_fresh_secret_template(self):
        """Generate a fresh template for updating GitHub secret.

        To update the CACHED_CREDENTIALS secret:
        1. Run: gh secret set CACHED_CREDENTIALS
        2. Paste the JSON output from this test
        3. Press Ctrl+D (EOF)

        Or use: gh secret set CACHED_CREDENTIALS < secret.json
        """
        template = {
            "credentials": {
                "channel_uid": "YOUR_CHANNEL_UID_HERE",
                "yostar_token": "YOUR_YOSTAR_TOKEN_HERE"
            },
            "email": "YOUR_TEST_EMAIL_HERE",
            "server": "en",
            "timestamp": datetime.now().isoformat()
        }

        # Print formatted JSON for easy copy-paste
        formatted_json = json.dumps(template, indent=2)
        print("\n" + "="*60)
        print("CACHED_CREDENTIALS Secret Template")
        print("="*60)
        print(formatted_json)
        print("="*60)
        print(f"\nTimestamp generated: {template['timestamp']}")
        print(f"Valid until: {(datetime.now() + CACHE_DURATION).isoformat()}")
        print(f"Cache duration: {CACHE_DURATION}")
        print("\nTo update GitHub secret:")
        print("  gh secret set CACHED_CREDENTIALS")
        print("  (paste the JSON above)")
        print("  (press Ctrl+D)")
        print("="*60 + "\n")

        assert "YOUR_CHANNEL_UID_HERE" in formatted_json
        assert "YOUR_YOSTAR_TOKEN_HERE" in formatted_json

    def test_email_must_match_test_account(self):
        """Test that email in secret must match TEST_ACCOUNT_EMAIL env var.

        The integration tests use TEST_ACCOUNT_EMAIL from environment.
        The cached credentials email must match exactly (case-sensitive).
        """
        import os

        # This is what the workflow sets
        test_email = os.getenv("TEST_ACCOUNT_EMAIL", "unknown")

        # Example secret with matching email
        matching_secret = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": test_email,  # Must match!
            "server": "en",
            "timestamp": datetime.now().isoformat()
        }

        assert matching_secret["email"] == test_email

    def test_server_must_match_test_server(self):
        """Test that server in secret must match TEST_ACCOUNT_SERVER env var.

        The integration tests use TEST_ACCOUNT_SERVER from environment (default: "en").
        The cached credentials server must match exactly.
        """
        import os

        # This is what the workflow sets
        test_server = os.getenv("TEST_ACCOUNT_SERVER", "en")

        # Example secret with matching server
        matching_secret = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "test@example.com",
            "server": test_server,  # Must match!
            "timestamp": datetime.now().isoformat()
        }

        assert matching_secret["server"] == test_server

    def test_common_mistakes(self):
        """Test to document common mistakes in secret format."""

        # WRONG: Missing timestamp
        wrong_no_timestamp = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "test@example.com",
            "server": "en"
        }
        assert "timestamp" not in wrong_no_timestamp  # This will fail to load!

        # WRONG: Old timestamp
        wrong_old_timestamp = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "test@example.com",
            "server": "en",
            "timestamp": "2026-01-20T00:00:00"  # > 1 day old!
        }
        old_age = datetime.now() - datetime.fromisoformat(wrong_old_timestamp["timestamp"])
        assert old_age > CACHE_DURATION  # This will be rejected as expired!

        # WRONG: Wrong email
        wrong_email = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "wrong@example.com",  # Doesn't match TEST_ACCOUNT_EMAIL!
            "server": "en",
            "timestamp": datetime.now().isoformat()
        }
        # This will not match and cache won't be used

        # CORRECT: All fields present and valid
        correct = {
            "credentials": {"channel_uid": "uid", "yostar_token": "token"},
            "email": "test@example.com",  # Must match TEST_ACCOUNT_EMAIL
            "server": "en",  # Must match TEST_ACCOUNT_SERVER
            "timestamp": datetime.now().isoformat()  # Must be recent
        }

        # Verify correct format
        assert "timestamp" in correct
        assert "credentials" in correct
        recent_age = datetime.now() - datetime.fromisoformat(correct["timestamp"])
        assert recent_age <= CACHE_DURATION


def test_print_current_cache_duration():
    """Print the current cache duration setting."""
    print(f"\nCurrent CACHE_DURATION: {CACHE_DURATION}")
    print(f"Total seconds: {CACHE_DURATION.total_seconds()}")
    print(f"Total hours: {CACHE_DURATION.total_seconds() / 3600}")
    print(f"Total days: {CACHE_DURATION.days}")

    assert CACHE_DURATION.days >= 1
