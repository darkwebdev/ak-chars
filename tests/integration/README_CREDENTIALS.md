# Credential Caching for Integration Tests

## Problem

Integration tests authenticate with Yostar game servers to test the API. However, Yostar has strict rate limits on authentication requests. Requesting auth codes too frequently causes errors:

```
{"Code": 100302, "Msg": "邮件发送频率上限,错误代码:1"}
```

Translation: "Email sending frequency limit exceeded, error code: 1"

## Solution

Cache valid game credentials in a GitHub secret (`CACHED_CREDENTIALS`) so tests can reuse them instead of requesting new auth codes every run.

## How It Works

1. **First successful auth**: Tests authenticate and save credentials to cache
2. **Subsequent runs**: Tests load cached credentials if valid
3. **Cache validation**: Credentials are checked for:
   - File exists
   - Email matches `TEST_ACCOUNT_EMAIL`
   - Server matches `TEST_ACCOUNT_SERVER` (default: "en")
   - Timestamp is within `CACHE_DURATION` (7 days)

## Cache File Format

The `CACHED_CREDENTIALS` GitHub secret must be valid JSON:

```json
{
  "credentials": {
    "channel_uid": "your_actual_channel_uid",
    "yostar_token": "your_actual_yostar_token"
  },
  "email": "your_test_account@example.com",
  "server": "en",
  "timestamp": "2026-01-24T12:00:00.000000"
}
```

**CRITICAL**: The timestamp must be within the last 7 days or the cache is considered expired.

## Updating the GitHub Secret

### Method 1: Using gh CLI

```bash
# Generate a fresh template
pytest tests/integration/test_github_secret_format.py::TestGitHubSecretFormat::test_generate_fresh_secret_template -v -s

# Copy the JSON output and update the placeholders:
# - YOUR_CHANNEL_UID_HERE → actual channel_uid from game account
# - YOUR_YOSTAR_TOKEN_HERE → actual yostar_token from game account
# - YOUR_TEST_EMAIL_HERE → must match TEST_ACCOUNT_EMAIL secret

# Update the secret
gh secret set CACHED_CREDENTIALS
# (paste the JSON)
# (press Ctrl+D)
```

### Method 2: GitHub Web UI

1. Go to repository Settings → Secrets and variables → Actions
2. Edit `CACHED_CREDENTIALS`
3. Paste the JSON (update placeholders with real values)
4. Save

## Getting Valid Credentials

If you need to get fresh credentials:

1. **Run auth flow locally**:
   ```bash
   # Set environment variables
   export TEST_ACCOUNT_EMAIL="your_test_account@example.com"
   export TEST_ACCOUNT_EMAIL_PASSWORD="your_email_password"
   export API_BASE_URL="https://ak-chars-api.fly.dev"

   # Run a single integration test to generate credentials
   pytest tests/integration/test_auth_flow.py::test_complete_auth_flow -v
   ```

2. **Check the cache file**:
   ```bash
   cat tests/integration/.credentials_cache.json
   ```

3. **Copy the content** to update the GitHub secret

## Troubleshooting

### Cache Not Being Used

Check the GitHub Actions logs for the "Debug credentials cache" step:

```bash
gh run view <run-id> --log | grep -A 10 "Debug credentials cache"
```

Common issues:

1. **Timestamp too old** (> 7 days)
   - Solution: Update secret with fresh timestamp

2. **Email mismatch**
   - The `email` field must exactly match `TEST_ACCOUNT_EMAIL` secret
   - Check: `gh secret list` and verify email values match

3. **Server mismatch**
   - The `server` field must match `TEST_ACCOUNT_SERVER` (default: "en")

4. **Malformed JSON**
   - Validate JSON: `echo '$SECRET_CONTENT' | jq .`

5. **Empty or missing secret**
   - File size should be > 200 bytes
   - Check the debug output for file size

### Tests Still Failing with Valid Cache

1. **Rate limit already triggered**: Wait 1-2 hours before retrying
2. **Credentials expired**: Game credentials may have expired server-side
3. **Account issues**: Verify test account is still active

## Testing Locally

Run the credential cache tests to verify everything works:

```bash
# Run all credential cache tests
pytest tests/integration/test_credential_cache.py -v

# Run format validation tests
pytest tests/integration/test_github_secret_format.py -v

# Check current cache duration
pytest tests/integration/test_github_secret_format.py::test_print_current_cache_duration -v -s
```

## Configuration

Cache duration is configured in `tests/integration/credential_cache.py`:

```python
CACHE_DURATION = timedelta(days=7)  # Credentials valid for 7 days
```

To adjust:
1. Edit `CACHE_DURATION` value
2. Run tests to verify: `pytest tests/integration/test_credential_cache.py -v`
3. Update any cached credentials (timestamp must be within new duration)

## GitHub Actions Workflow

The integration tests workflow (`.github/workflows/integration-tests.yml`) sets up the cache:

```yaml
- name: Set up credentials cache
  run: |
    mkdir -p tests/integration
    echo '${{ secrets.CACHED_CREDENTIALS }}' > tests/integration/.credentials_cache.json
```

The debug step verifies the cache file is created and has content.

## Best Practices

1. **Update credentials weekly**: Set a reminder to refresh the timestamp every 7 days
2. **Monitor test runs**: Check for rate limit errors indicating cache expiration
3. **Protect the secret**: Never commit `.credentials_cache.json` to git (it's in `.gitignore`)
4. **Use test account**: Don't use your personal game account for integration tests
