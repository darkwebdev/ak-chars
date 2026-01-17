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
        """Test that tokens are redacted in JSON."""
        input_json = json.dumps({
            "channel_uid": "abc123xyz",
            "yostar_token": "supersecrettoken",
            "email": "user@example.com"
        })
        
        result = sanitize_sensitive_data(input_json)
        result_data = json.loads(result)
        
        assert result_data["channel_uid"] == "***REDACTED***"
        assert result_data["yostar_token"] == "***REDACTED***"
        assert result_data["email"] == "user@example.com"
    
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
        
        assert result_data["data"]["channel_uid"] == "***REDACTED***"
        assert result_data["data"]["token"] == "***REDACTED***"
        assert result_data["data"]["user"]["api_key"] == "***REDACTED***"
        assert result_data["data"]["user"]["email"] == "test@example.com"
    
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
        
        assert result_data["users"][0]["token"] == "***REDACTED***"
        assert result_data["users"][1]["password"] == "***REDACTED***"
        assert result_data["users"][0]["name"] == "Alice"
        assert result_data["users"][1]["name"] == "Bob"
    
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
        
        assert result_data["Yostar_Token"] == "***REDACTED***"
        assert result_data["CHANNEL_UID"] == "***REDACTED***"
        assert result_data["Password"] == "***REDACTED***"
        assert result_data["NickName"] == "SafeValue"
    
    def test_sanitize_text_with_regex(self):
        """Test regex-based sanitization for non-JSON text."""
        input_text = 'Log: "yostar_token": "abc123" and "password": "secret"'
        
        result = sanitize_sensitive_data(input_text)
        
        assert "abc123" not in result
        assert "secret" not in result
        assert "***REDACTED***" in result
    
    def test_sanitize_all_sensitive_fields(self):
        """Test that all sensitive fields are redacted."""
        sensitive_fields = [
            "yostar_token", "token", "channel_uid", "channelUid",
            "password", "secret", "api_key", "apiKey",
            "code", "authorization", "auth"
        ]
        
        for field in sensitive_fields:
            input_json = json.dumps({field: "secret_value", "safe": "ok"})
            result = sanitize_sensitive_data(input_json)
            result_data = json.loads(result)
            
            assert result_data[field] == "***REDACTED***", f"Field {field} should be redacted"
            assert result_data["safe"] == "ok"
    
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
        
        assert result_data["nickName"] == "Player123"
        assert result_data["level"] == 107
        assert result_data["server"] == "en"
        assert result_data["charId"] == "char_002_amiya"
        assert result_data["yostar_token"] == "***REDACTED***"


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
        
        assert result["content-type"] == "application/json"
        assert result["authorization"] == "***REDACTED***"
        assert result["user-agent"] == "Mozilla/5.0"
    
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
        
        assert result["authorization"] == "***REDACTED***"
        assert result["cookie"] == "***REDACTED***"
        assert result["x-api-key"] == "***REDACTED***"
        assert result["api-key"] == "***REDACTED***"
        assert result["content-type"] == "application/json"
    
    def test_sanitize_case_insensitive_headers(self):
        """Test that header matching is case-insensitive."""
        headers = {
            "Authorization": "Bearer token",
            "COOKIE": "session=abc",
            "X-Api-Key": "key123"
        }
        
        result = sanitize_headers(headers)
        
        assert result["Authorization"] == "***REDACTED***"
        assert result["COOKIE"] == "***REDACTED***"
        assert result["X-Api-Key"] == "***REDACTED***"
    
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
