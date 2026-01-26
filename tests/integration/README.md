# Integration Tests

Integration tests for the Arknights server authentication and API functionality. These tests authenticate with real Arknights servers using test accounts and validate API responses with live data.

## Overview

**Email Provider:** [Mail.tm](https://mail.tm)
**Test Framework:** pytest with async support
**Strategy:** One manually created test account, reused across all tests
**Scope:** Authentication flow, roster APIs, GraphQL queries

## Prerequisites

### 1. Create Mail.tm Account

1. Visit https://mail.tm
2. Click "Register" or use the API to create an account
3. Choose a username (e.g., `aktest123`)
4. Set a strong password
5. Your email will be `username@mail.tm` (e.g., `aktest123@mail.tm`)
6. Save these credentials securely

### 2. Create Arknights Test Account

1. Open Arknights game
2. Create a new account using the Mail.tm email
3. Complete initial tutorial/setup
4. This account will be used for all integration tests

**Important:** Use a dedicated test account, not your personal account.

### 3. Configure Environment Variables

Create a `.env` file in the repository root (or set environment variables):

```bash
# Mail.tm credentials
TEST_ACCOUNT_EMAIL=your-username@mail.tm
TEST_ACCOUNT_EMAIL_PASSWORD=your-mail-tm-password

# Arknights server (en, jp, kr, cn)
TEST_ACCOUNT_SERVER=en

# Optional: API base URL (defaults to http://127.0.0.1:8000)
API_BASE_URL=http://127.0.0.1:8000
```

**For CI (GitHub Actions):**

Configure the following secrets in repository settings → Secrets and variables → Actions:

- `TEST_ACCOUNT_EMAIL` - Your Mail.tm email address
- `TEST_ACCOUNT_EMAIL_PASSWORD` - Your Mail.tm password

## Automatic Credential Management

**New in 2026:** Tests now use an **automatic credential caching system** to avoid rate limiting:

### How Caching Works

1. **First Run**: Tests perform full auth flow and cache credentials for 24 hours
2. **Subsequent Runs**: Tests use cached credentials (no email verification needed)
3. **Daily Refresh**: Cache expires after 24 hours, triggering automatic refresh
4. **Retry Logic**: 3 retry attempts with exponential backoff (5s, 10s, 15s)
5. **No Manual Steps**: Everything happens automatically during test execution

### GitHub Actions Integration

The workflow automatically:
- Checks cache age before running tests
- Deletes expired cache to trigger refresh
- Detects when credentials were refreshed during tests
- Uploads refreshed credentials as artifacts for secret update

**To update the GitHub secret after automatic refresh:**
```bash
.github/scripts/update-cached-credentials.sh
```

### Cache File Structure

```json
{
  "email": "test@mail.tm",
  "server": "en",
  "timestamp": "2026-01-26T15:08:08.998492",
  "credentials": {
    "channel_uid": "...",
    "yostar_token": "..."
  }
}
```

**Cache Duration:** 1 day (configured in `credential_cache.py`)
**Cache Location:** `tests/integration/.credentials_cache.json` (gitignored)
**GitHub Secret:** `CACHED_CREDENTIALS` (manually updated when refreshed)

## How It Works

### Mail.tm API Flow

1. **Login:** Tests authenticate with Mail.tm API using credentials
2. **Get JWT Token:** Receive token for accessing mailbox
3. **Request Game Code:** Trigger Yostar to send verification email
4. **Poll Messages:** Check Mail.tm inbox for new emails
5. **Extract Code:** Parse 6-digit verification code from email
6. **Exchange Token:** Trade code for Arknights game credentials
7. **Use Credentials:** Make API calls with authenticated tokens

### Test Structure

```
tests/integration/
├── __init__.py              # Package marker
├── conftest.py             # pytest fixtures and configuration
├── email_helper.py         # Mail.tm API client and code fetcher
├── test_auth_flow.py       # Authentication flow tests
├── test_roster_live.py     # Live data validation tests
└── README.md               # This file
```

### Key Components

**MailTmClient** (`email_helper.py`)
- Handles Mail.tm REST API communication
- Methods: `login()`, `get_messages()`, `get_message()`

**MailTmCodeFetcher** (`email_helper.py`)
- Polls inbox for Yostar emails
- Extracts 6-digit verification codes
- Configurable timeout and polling interval

**pytest Fixtures** (`conftest.py`)
- `test_email`: Mail.tm email address from env
- `test_email_password`: Mail.tm password from env
- `mail_tm_client`: HTTP client for Mail.tm API
- `mail_tm_token`: Session-scoped JWT token (cached)
- `email_fetcher`: Code extraction utility
- `game_credentials`: Session-scoped game auth (cached)
- `api_client`: HTTP client for Arknights API

## Running Tests

### Install Dependencies

```bash
pip install -r server/requirements.txt
```

### Run All Integration Tests

```bash
pytest tests/integration/ -v -m integration
```

### Run Specific Test File

```bash
pytest tests/integration/test_auth_flow.py -v
pytest tests/integration/test_roster_live.py -v
```

### Run Specific Test

```bash
pytest tests/integration/test_auth_flow.py::test_complete_auth_flow -v
```

### Skip Integration Tests

```bash
pytest tests/ -v -m "not integration"
```

### With Coverage

```bash
pytest tests/integration/ -v --cov=server --cov-report=html
```

## CI Integration

Integration tests run on a **daily schedule** in GitHub Actions to avoid rate limiting and minimize API load.

**Workflow:** `.github/workflows/integration-tests.yml`

**Schedule:** Daily at 9 AM UTC

**Manual Trigger:** Available via workflow_dispatch

**Required Secrets:**
- `TEST_ACCOUNT_EMAIL`
- `TEST_ACCOUNT_EMAIL_PASSWORD`

## Troubleshooting

### Tests Skip with "requires TEST_ACCOUNT_EMAIL"

**Cause:** Environment variables not set
**Fix:** Create `.env` file or export variables:

```bash
export TEST_ACCOUNT_EMAIL=your-email@mail.tm
export TEST_ACCOUNT_EMAIL_PASSWORD=your-password
```

### TimeoutError: No verification code received

**Possible causes:**
1. **Email delays:** Yostar emails can take 30-90 seconds
2. **Wrong email:** Check TEST_ACCOUNT_EMAIL matches game account
3. **Mail.tm issues:** Check https://mail.tm status
4. **Already sent:** Code was sent to a previous email (check inbox manually)

**Fix:**
- Increase timeout in test: `wait_for_code(timeout=120)`
- Check Mail.tm inbox manually at https://mail.tm
- Verify game account uses the correct email

### httpx.HTTPError or 401 Unauthorized (Mail.tm)

**Cause:** Invalid Mail.tm credentials or expired token
**Fix:** Verify TEST_ACCOUNT_EMAIL_PASSWORD is correct:

```bash
curl -X POST https://api.mail.tm/token \
  -H "Content-Type: application/json" \
  -d '{"address":"your-email@mail.tm","password":"your-password"}'
```

### Invalid credentials rejected (Arknights API)

**Cause:** Token expired or invalid
**Fix:**
- Session-scoped fixture caches credentials once per test run
- Restart pytest to force re-authentication
- Verify game account is active and not banned

### Rate limiting from Yostar

**Cause:** Too many authentication requests
**Fix:**
- Use session-scoped `game_credentials` fixture (already implemented)
- Don't run tests too frequently (CI runs daily)
- Wait 5-10 minutes between manual test runs

### Mail.tm API rate limiting

**Cause:** Polling too aggressively
**Fix:** Increase `poll_interval` in `wait_for_code()`:

```python
code = await email_fetcher.wait_for_code(timeout=90, poll_interval=10)
```

## Security Notes

1. **Never commit credentials:** `.env` is gitignored
2. **Use GitHub Secrets:** For CI, store credentials in encrypted secrets
3. **Dedicated test account:** Don't use personal Arknights account
4. **Log sanitization:** Tokens are automatically sanitized in logs (see `tests/test_sanitization.py`)
5. **Rotate passwords:** Periodically update Mail.tm password

## Architecture Decisions

### Why Mail.tm?

- **Simple REST API:** No IMAP complexity
- **No phone verification:** Easy to automate
- **Free tier:** No cost for testing
- **Reliable:** Works consistently for automation
- **Python-friendly:** Use existing httpx library

### Why Session-Scoped Credentials?

- **Avoid rate limiting:** Authenticate once per test session
- **Faster tests:** Reuse credentials across tests
- **Consistent state:** Same account data for all tests

### Why Daily CI Schedule?

- **Minimize API load:** Don't overwhelm Yostar servers
- **Avoid rate limits:** Spread out authentication requests
- **Catch regressions:** Daily validation is sufficient for integration tests

## References

- **Mail.tm API Docs:** https://docs.mail.tm/
- **pytest-asyncio:** https://github.com/pytest-dev/pytest-asyncio
- **pytest-timeout:** https://github.com/pytest-dev/pytest-timeout
- **Arknights API:** Internal server endpoints (see `server/auth.py`)
