"""Tests for log sanitization functions.

This is a standalone test that duplicates the sanitization logic
to verify it works correctly without requiring server dependencies.
"""
import json
import re


def sanitize_sensitive_data(text: str) -> str:
    """Mask sensitive data in logs to prevent credential leakage."""
    try:
        data = json.loads(text)
        sensitive_fields = {
            'yostar_token', 'token', 'channel_uid', 'channelUid',
            'password', 'secret', 'api_key', 'apiKey',
            'code', 'authorization', 'auth'
        }
        
        def mask_dict(obj):
            if isinstance(obj, dict):
                return {
                    k: '***REDACTED***' if k.lower() in {f.lower() for f in sensitive_fields}
                    else mask_dict(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [mask_dict(item) for item in obj]
            return obj
        
        masked = mask_dict(data)
        return json.dumps(masked)
    except Exception:
        patterns = [
            (r'"(yostar_token|token|channel_uid|channelUid|password|secret|api_key|apiKey|code|authorization)"\s*:\s*"[^"]*"', r'"\1": "***REDACTED***"'),
            (r"'(yostar_token|token|channel_uid|channelUid|password|secret|api_key|apiKey|code|authorization)'\s*:\s*'[^']*'", r"'\1': '***REDACTED***'"),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


def sanitize_headers(headers: dict) -> dict:
    """Remove sensitive headers from logs."""
    safe_headers = {}
    sensitive_keys = {'authorization', 'cookie', 'x-api-key', 'api-key'}
    for key, value in headers.items():
        if key.lower() in sensitive_keys:
            safe_headers[key] = '***REDACTED***'
        else:
            safe_headers[key] = value
    return safe_headers


def test_sanitize_json_with_sensitive_fields():
    """Test that sensitive fields in JSON are redacted."""
    input_json = json.dumps({
        "channel_uid": "abc123xyz",
        "yostar_token": "supersecrettoken",
        "email": "user@example.com",
        "server": "en"
    })
    
    result = sanitize_sensitive_data(input_json)
    result_data = json.loads(result)
    
    assert result_data["channel_uid"] == "***REDACTED***"
    assert result_data["yostar_token"] == "***REDACTED***"
    assert result_data["email"] == "user@example.com"  # not sensitive
    assert result_data["server"] == "en"  # not sensitive


def test_sanitize_nested_json():
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


def test_sanitize_text_with_regex():
    """Test regex-based sanitization for non-JSON text."""
    input_text = 'Some log with "yostar_token": "abc123" and "password": "secret"'
    
    result = sanitize_sensitive_data(input_text)
    
    assert "abc123" not in result
    assert "secret" not in result
    assert "***REDACTED***" in result


def test_sanitize_headers():
    """Test that sensitive headers are redacted."""
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer secret_token",
        "x-api-key": "apikey123",
        "user-agent": "Mozilla/5.0"
    }
    
    result = sanitize_headers(headers)
    
    assert result["content-type"] == "application/json"
    assert result["authorization"] == "***REDACTED***"
    assert result["x-api-key"] == "***REDACTED***"
    assert result["user-agent"] == "Mozilla/5.0"


def test_sanitize_case_insensitive():
    """Test that field matching is case-insensitive."""
    input_json = json.dumps({
        "Yostar_Token": "secret1",
        "CHANNEL_UID": "secret2",
        "Password": "secret3"
    })
    
    result = sanitize_sensitive_data(input_json)
    result_data = json.loads(result)
    
    assert result_data["Yostar_Token"] == "***REDACTED***"
    assert result_data["CHANNEL_UID"] == "***REDACTED***"
    assert result_data["Password"] == "***REDACTED***"


def test_sanitize_list_of_objects():
    """Test sanitization of arrays containing objects."""
    input_json = json.dumps({
        "users": [
            {"name": "Alice", "token": "secret1"},
            {"name": "Bob", "token": "secret2"}
        ]
    })
    
    result = sanitize_sensitive_data(input_json)
    result_data = json.loads(result)
    
    assert result_data["users"][0]["token"] == "***REDACTED***"
    assert result_data["users"][1]["token"] == "***REDACTED***"
    assert result_data["users"][0]["name"] == "Alice"
    assert result_data["users"][1]["name"] == "Bob"


if __name__ == "__main__":
    test_sanitize_json_with_sensitive_fields()
    test_sanitize_nested_json()
    test_sanitize_text_with_regex()
    test_sanitize_headers()
    test_sanitize_case_insensitive()
    test_sanitize_list_of_objects()
    print("✓ All sanitization tests passed!")
