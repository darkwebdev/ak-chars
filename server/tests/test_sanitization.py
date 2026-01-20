"""Tests for log sanitization functions."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import pytest
from server.main import sanitize_sensitive_data, sanitize_headers


class TestSanitizeSensitiveData:
    """Tests for sanitize_sensitive_data function."""
    
    def test_sanitize_json_with_tokens(self):
        """Test that tokens and emails are redacted in JSON."""
        input_json = json.dumps({
            "channel_uid": "abc123xyz",
            "yostar_token": "supersecrettoken",
            "email": "user@example.com"
        })

        result = sanitize_sensitive_data(input_json)
        result_data = json.loads(result)

        # Verify sensitive values are NOT in the output
        assert "abc123xyz" not in result
        assert "supersecrettoken" not in result
        assert "user@example.com" not in result

        # Verify fields exist but are changed
        assert result_data["channel_uid"] != "abc123xyz"
        assert result_data["yostar_token"] != "supersecrettoken"
        assert result_data["email"] != "user@example.com"
    
    def test_sanitize_nested_json(self):
        """Test sanitization of nested JSON structures."""
        input_json = json.dumps({
            "ok": True,
            "data": {
                "channel_uid": "abc123",
                "token": "secret",
                "user": {
                    "email": "test@example.com",
                    "api_key": "apikey123"
                }
            }
        })

        result = sanitize_sensitive_data(input_json)
        result_data = json.loads(result)

        # Verify sensitive values are NOT in the output
        assert "abc123" not in result
        assert "secret" not in result
        assert "test@example.com" not in result
        assert "apikey123" not in result

        # Verify ok flag is preserved
        assert result_data["ok"] is True

        # Verify fields exist but are changed
        assert result_data["data"]["channel_uid"] != "abc123"
        assert result_data["data"]["token"] != "secret"
        assert result_data["data"]["user"]["api_key"] != "apikey123"
        assert result_data["data"]["user"]["email"] != "test@example.com"
    
    def test_sanitize_list_of_objects(self):
        """Test sanitization of arrays containing objects."""
        input_json = json.dumps({
            "users": [
                {"name": "Alice", "token": "secret1"},
                {"name": "Bob", "password": "secret2"}
            ]
        })

        result = sanitize_sensitive_data(input_json)
        result_data = json.loads(result)

        # Verify sensitive values are NOT in the output
        assert "secret1" not in result
        assert "secret2" not in result

        # Verify safe values are preserved
        assert result_data["users"][0]["name"] == "Alice"
        assert result_data["users"][1]["name"] == "Bob"

        # Verify sensitive fields exist but are changed
        assert result_data["users"][0]["token"] != "secret1"
        assert result_data["users"][1]["password"] != "secret2"
    
    def test_sanitize_case_insensitive(self):
        """Test that field matching is case-insensitive."""
        input_json = json.dumps({
            "Yostar_Token": "secret1",
            "CHANNEL_UID": "secret2",
            "Password": "secret3",
            "NickName": "SafeValue"
        })

        result = sanitize_sensitive_data(input_json)
        result_data = json.loads(result)

        # Verify sensitive values are NOT in the output
        assert "secret1" not in result
        assert "secret2" not in result
        assert "secret3" not in result

        # Verify safe value is preserved
        assert result_data["NickName"] == "SafeValue"

        # Verify sensitive fields exist but are changed
        assert result_data["Yostar_Token"] != "secret1"
        assert result_data["CHANNEL_UID"] != "secret2"
        assert result_data["Password"] != "secret3"
    
    def test_sanitize_text_with_regex(self):
        """Test regex-based sanitization for non-JSON text."""
        input_text = 'Log: "yostar_token": "abc123" and "password": "secret"'

        result = sanitize_sensitive_data(input_text)

        # Verify sensitive values are NOT in the output
        assert "abc123" not in result
        assert "secret" not in result

        # Verify field names are preserved (structure intact)
        assert "yostar_token" in result
        assert "password" in result
    
    def test_sanitize_all_sensitive_fields(self):
        """Test that all sensitive fields are redacted."""
        sensitive_fields = [
            "yostar_token", "token", "channel_uid", "channelUid",
            "password", "secret", "api_key", "apiKey",
            "code", "authorization", "auth", "email"
        ]

        for field in sensitive_fields:
            input_json = json.dumps({field: "secret_value", "safe": "ok"})
            result = sanitize_sensitive_data(input_json)
            result_data = json.loads(result)

            # Verify sensitive value is NOT in the output
            assert "secret_value" not in result, f"Field {field} value should not be in output"

            # Verify safe value is preserved
            assert result_data["safe"] == "ok"

            # Verify field exists but value is changed
            assert result_data[field] != "secret_value", f"Field {field} should be redacted"
    
    def test_sanitize_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        input_json = json.dumps({
            "nickName": "Player123",
            "level": 107,
            "server": "en",
            "charId": "char_002_amiya",
            "yostar_token": "secret"
        })

        result = sanitize_sensitive_data(input_json)
        result_data = json.loads(result)

        # Verify non-sensitive data is preserved
        assert result_data["nickName"] == "Player123"
        assert result_data["level"] == 107
        assert result_data["server"] == "en"
        assert result_data["charId"] == "char_002_amiya"

        # Verify sensitive value is NOT in the output
        assert "secret" not in result

        # Verify sensitive field exists but value is changed
        assert result_data["yostar_token"] != "secret"


class TestSanitizeHeaders:
    """Tests for sanitize_headers function."""
    
    def test_sanitize_authorization_header(self):
        """Test that authorization header is redacted."""
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer secret_token",
            "user-agent": "Mozilla/5.0"
        }

        result = sanitize_headers(headers)

        # Verify safe headers are preserved
        assert result["content-type"] == "application/json"
        assert result["user-agent"] == "Mozilla/5.0"

        # Verify sensitive value is NOT in the result
        assert "secret_token" not in str(result)

        # Verify header exists but value is changed
        assert result["authorization"] != "Bearer secret_token"
    
    def test_sanitize_multiple_sensitive_headers(self):
        """Test that all sensitive headers are redacted."""
        headers = {
            "authorization": "Bearer token",
            "cookie": "session=abc123",
            "x-api-key": "apikey123",
            "api-key": "anotherkey",
            "content-type": "application/json"
        }

        result = sanitize_headers(headers)

        # Verify sensitive values are NOT in the result
        result_str = str(result)
        assert "Bearer token" not in result_str
        assert "session=abc123" not in result_str
        assert "apikey123" not in result_str
        assert "anotherkey" not in result_str

        # Verify safe header is preserved
        assert result["content-type"] == "application/json"

        # Verify sensitive headers exist but values are changed
        assert result["authorization"] != "Bearer token"
        assert result["cookie"] != "session=abc123"
        assert result["x-api-key"] != "apikey123"
        assert result["api-key"] != "anotherkey"
    
    def test_sanitize_case_insensitive_headers(self):
        """Test that header matching is case-insensitive."""
        headers = {
            "Authorization": "Bearer token",
            "COOKIE": "session=abc",
            "X-Api-Key": "key123"
        }

        result = sanitize_headers(headers)

        # Verify sensitive values are NOT in the result
        result_str = str(result)
        assert "Bearer token" not in result_str
        assert "session=abc" not in result_str
        assert "key123" not in result_str

        # Verify headers exist but values are changed
        assert result["Authorization"] != "Bearer token"
        assert result["COOKIE"] != "session=abc"
        assert result["X-Api-Key"] != "key123"
    
    def test_sanitize_empty_headers(self):
        """Test sanitization with empty headers."""
        headers = {}
        result = sanitize_headers(headers)
        assert result == {}
    
    def test_sanitize_preserves_safe_headers(self):
        """Test that non-sensitive headers are preserved."""
        headers = {
            "content-type": "application/json",
            "user-agent": "TestClient",
            "accept": "*/*",
            "host": "localhost:8000"
        }
        
        result = sanitize_headers(headers)
        
        assert result == headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
