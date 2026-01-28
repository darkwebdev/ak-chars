# Circuit Breaker for Rate Limiting

## Overview

This document describes the circuit breaker implementation that detects and handles Yostar API rate limiting in integration tests.

## Problem

The Yostar authentication API enforces strict rate limits on email verification code requests. When the limit is exceeded, the API returns:

```json
{
  "Code": 100302,
  "Msg": "邮件发送频率上限,错误代码:1"
}
```

**Translation**: "Email sending frequency limit exceeded, error code: 1"

Without the circuit breaker, the retry logic would continue attempting authentication 3 times with exponential backoff (5s, 10s, 15s), wasting time when the issue is rate limiting rather than a transient failure.

## Solution

### Circuit Breaker Function

Location: `tests/integration/conftest.py:20-61`

The `is_rate_limit_error()` function detects rate limit errors by checking for:

1. **Error code 100302** in the exception message
2. **Chinese text** "邮件发送频率" or "频率上限" in the message
3. **HTTP response body** containing error code or message (for HTTPStatusError)

```python
def is_rate_limit_error(error: Exception) -> bool:
    """Check if an error is a Yostar rate limit error."""
    error_str = str(error).lower()

    # Check for explicit error code
    if '100302' in error_str:
        return True

    # Check for Chinese rate limit message
    if '邮件发送频率' in error_str or '频率上限' in error_str:
        return True

    # For HTTPStatusError, check response body
    if isinstance(error, httpx.HTTPStatusError):
        try:
            body = error.response.json()
            # ... check body for error code or message
        except (json.JSONDecodeError, ValueError, AttributeError):
            pass

    return False
```

### Integration with Retry Logic

Location: `tests/integration/conftest.py:274-287`

When an error occurs during authentication, the circuit breaker checks if it's a rate limit error:

```python
except Exception as e:
    last_error = e
    logger.warning(f"Attempt {attempt} failed: {e}")

    # Circuit breaker: detect rate limiting and fail immediately
    if is_rate_limit_error(e):
        logger.error(
            "⚠️  RATE LIMIT DETECTED (error code 100302)\n"
            "The Yostar API has rate limited email code requests.\n"
            "This typically happens when too many codes are requested in a short time.\n"
            "Recommendation: Wait 1-2 hours before retrying, or use cached credentials.\n"
            f"Error details: {e}"
        )
        raise RuntimeError(
            "Yostar API rate limit exceeded (error code 100302). "
            "Please wait 1-2 hours before requesting new authentication codes. "
            "Consider using cached credentials or increasing cache duration."
        ) from e

    # Continue with normal retry logic for other errors
    if attempt < max_retries:
        wait_time = attempt * 5
        await asyncio.sleep(wait_time)
```

## Behavior

### Without Circuit Breaker

```
Attempt 1: Rate limited (100302)
  └─> Wait 5s
Attempt 2: Rate limited (100302)
  └─> Wait 10s
Attempt 3: Rate limited (100302)
  └─> Fail after ~15s total delay
```

### With Circuit Breaker

```
Attempt 1: Rate limited (100302)
  └─> Detect rate limit, fail immediately with clear message
  └─> Total delay: 0s
```

## Error Message

When rate limiting is detected, users see:

```
⚠️  RATE LIMIT DETECTED (error code 100302)
The Yostar API has rate limited email code requests.
This typically happens when too many codes are requested in a short time.
Recommendation: Wait 1-2 hours before retrying, or use cached credentials.

RuntimeError: Yostar API rate limit exceeded (error code 100302).
Please wait 1-2 hours before requesting new authentication codes.
Consider using cached credentials or increasing cache duration.
```

## Testing

### Test Suite

Location: `tests/integration/test_circuit_breaker.py`

The circuit breaker has comprehensive test coverage (11 tests):

1. ✓ Detects error code 100302 in exception message
2. ✓ Detects Chinese rate limit message
3. ✓ Detects partial Chinese message
4. ✓ Detects HTTP error with code in response body
5. ✓ Detects HTTP error with code in detail field
6. ✓ Ignores other HTTP errors
7. ✓ Handles non-JSON responses gracefully
8. ✓ Ignores generic exceptions
9. ✓ Ignores connection errors
10. ✓ Case-insensitive detection
11. ✓ Detects code in nested exception messages

### Running Tests

```bash
# Run circuit breaker tests only
pytest tests/integration/test_circuit_breaker.py -v

# Run all integration tests
pytest tests/integration/ -v
```

## Benefits

1. **Faster failure** - Immediately stops retrying when rate limited
2. **Clear messaging** - Users understand why authentication failed
3. **Actionable guidance** - Recommends using cached credentials or waiting
4. **Resource efficiency** - Doesn't waste time on retries that will fail
5. **Better debugging** - Distinguishes rate limiting from other errors

## Related Files

| File | Purpose |
|------|---------|
| `tests/integration/conftest.py` | Circuit breaker implementation |
| `tests/integration/test_circuit_breaker.py` | Test suite (11 tests) |
| `tests/integration/credential_cache.py` | Credential caching system |
| `tests/integration/README_CREDENTIALS.md` | Credential caching documentation |

## Recommendations

1. **Use credential caching** - Set `CACHE_DURATION` to 7 days to minimize auth requests
2. **Monitor cache age** - Ensure `CACHED_CREDENTIALS` secret is updated regularly
3. **Avoid repeated tests** - Don't run auth flow tests multiple times in succession
4. **Wait when rate limited** - Allow 1-2 hours before requesting new codes

## Future Improvements

1. **Exponential backoff for rate limits** - Instead of failing immediately, could wait longer (1 hour)
2. **Automatic cache refresh** - Update GitHub secret automatically when credentials refresh
3. **Rate limit tracking** - Track when rate limits occur and adjust cache duration dynamically
4. **Mock mode** - Add test mode that doesn't hit real Yostar API
