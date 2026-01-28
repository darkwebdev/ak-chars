"""Tests for rate limit circuit breaker logic."""

import pytest
import httpx
from unittest.mock import Mock
from .conftest import is_rate_limit_error


class TestCircuitBreaker:
    """Test suite for rate limit detection and circuit breaker."""

    def test_detects_error_code_100302_in_string(self):
        """Circuit breaker detects error code 100302 in exception message."""
        error = RuntimeError("Error code 100302 from Yostar API")
        assert is_rate_limit_error(error) is True

    def test_detects_chinese_rate_limit_message(self):
        """Circuit breaker detects Chinese rate limit message."""
        error = RuntimeError("邮件发送频率上限,错误代码:1")
        assert is_rate_limit_error(error) is True

    def test_detects_partial_chinese_message(self):
        """Circuit breaker detects partial Chinese message."""
        error = RuntimeError("API error: 频率上限")
        assert is_rate_limit_error(error) is True

    def test_detects_http_error_with_code_in_body(self):
        """Circuit breaker detects rate limit in HTTP response body."""
        # Create mock response with rate limit error
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.json.return_value = {
            "Code": 100302,
            "Msg": "邮件发送频率上限,错误代码:1"
        }

        error = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=response
        )

        assert is_rate_limit_error(error) is True

    def test_detects_http_error_with_code_in_message(self):
        """Circuit breaker detects rate limit in HTTP error detail."""
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.json.return_value = {
            "detail": "Error code 100302: Rate limit exceeded"
        }

        error = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=response
        )

        assert is_rate_limit_error(error) is True

    def test_ignores_other_http_errors(self):
        """Circuit breaker does not trigger on other HTTP errors."""
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.json.return_value = {
            "detail": "Internal server error"
        }

        error = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=response
        )

        assert is_rate_limit_error(error) is False

    def test_ignores_non_json_responses(self):
        """Circuit breaker handles non-JSON responses gracefully."""
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.json.side_effect = ValueError("Not JSON")

        error = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=response
        )

        assert is_rate_limit_error(error) is False

    def test_ignores_generic_exceptions(self):
        """Circuit breaker does not trigger on unrelated exceptions."""
        error = ValueError("Some other error")
        assert is_rate_limit_error(error) is False

    def test_ignores_connection_errors(self):
        """Circuit breaker does not trigger on connection errors."""
        error = httpx.ConnectError("Connection refused")
        assert is_rate_limit_error(error) is False

    def test_case_insensitive_detection(self):
        """Circuit breaker detection is case-insensitive for error codes."""
        error = RuntimeError("ERROR CODE: 100302")
        assert is_rate_limit_error(error) is True

    def test_detects_code_in_nested_message(self):
        """Circuit breaker detects error code in nested exception messages."""
        inner = RuntimeError("Yostar API error 100302")
        outer = RuntimeError(f"Authentication failed: {inner}")
        assert is_rate_limit_error(outer) is True
