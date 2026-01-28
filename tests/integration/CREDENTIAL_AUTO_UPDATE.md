# Automatic Credential Update Workflow

## Overview

This document describes the automated credential update system that ensures integration tests always have fresh credentials without manual intervention.

## Problem Solved

**Previous Issue**:
- Integration tests would fail when credentials expired (> 1 day old)
- Required manual secret update via GitHub UI or CLI
- Tests wouldn't pass until the next day after credential refresh
- "Chicken and egg" problem: needed passing tests to get fresh credentials

**Current Solution**:
- Tests automatically refresh and update credentials in the same run
- No manual intervention required
- Tests pass immediately after credential refresh

---

## How It Works

### Test Execution Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. Load CACHED_CREDENTIALS secret                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 2. Validate cache (is timestamp < 1 day old?)      │
└─────────────┬──────────────┬────────────────────────┘
              │              │
            Valid         Expired
              │              │
              ▼              ▼
    ┌─────────────┐   ┌──────────────┐
    │ Use cache   │   │ Delete cache │
    └──────┬──────┘   └──────┬───────┘
           │                 │
           └────────┬────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│ 3. Run auth tests (test_auth_flow.py)              │
│    - If cache valid: skip (cached creds used)      │
│    - If cache expired: perform full auth flow      │
│      → Request code from Yostar API                │
│      → Get token from email                        │
│      → Save to .credentials_cache.json             │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 4. Check if credentials were refreshed              │
│    (timestamp age < 5 minutes?)                     │
└─────────────┬──────────────┬────────────────────────┘
              │              │
            YES             NO
              │              │
              ▼              ▼
    ┌──────────────────┐   Skip update
    │ Auto-update      │
    │ CACHED_          │
    │ CREDENTIALS      │
    │ secret via       │
    │ gh CLI           │
    └────────┬─────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ 5. Run remaining integration tests                  │
│    - test_roster_live.py                            │
│    - test_circuit_breaker.py                        │
│    - test_credential_cache.py                       │
│    - test_github_secret_format.py                   │
│    All tests use fresh credentials ✓                │
└─────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Auth Tests Run First

**Location**: `.github/workflows/integration-tests-new.yml:97-105`

```yaml
- name: Run auth tests first (to refresh credentials if needed)
  run: |
    echo "🔐 Running authentication tests to ensure credentials are fresh..."
    pytest tests/integration/test_auth_flow.py -v --timeout=300 --tb=short || echo "⚠️  Auth tests had failures, continuing..."
```

**Why first?**
- Detects expired credentials immediately
- Refreshes credentials before other tests need them
- Other tests can use fresh credentials in the same run

### 2. Automatic Secret Update

**Location**: `.github/workflows/integration-tests-new.yml:107-179`

After auth tests complete, the workflow:
1. Checks if `.credentials_cache.json` exists
2. Reads the timestamp
3. If age < 5 minutes → credentials were just refreshed
4. **Automatically updates** the `CACHED_CREDENTIALS` secret via `gh secret set`

```python
# Automatically update the secret
subprocess.run(
    ['gh', 'secret', 'set', 'CACHED_CREDENTIALS'],
    input=credentials_json.encode(),
    capture_output=True,
    check=True
)
```

**Permissions**: Workflow has `secrets: write` permission (line 15)

### 3. Remaining Tests Use Fresh Credentials

**Location**: `.github/workflows/integration-tests-new.yml:181-191`

```yaml
- name: Run remaining integration tests
  run: |
    echo "🧪 Running remaining integration tests with fresh credentials..."
    pytest tests/integration/ -v -m integration --timeout=300 --tb=short \
      --ignore=tests/integration/test_auth_flow.py
```

**Key point**: `--ignore=tests/integration/test_auth_flow.py` prevents re-running auth tests

---

## Workflows with Auto-Update

### 1. Integration Tests (`integration-tests-new.yml`)

**Trigger**:
- Daily at 9 AM UTC
- Manual via workflow_dispatch

**Steps**:
1. Run auth tests → refresh if needed
2. Auto-update secret if refreshed
3. Run remaining tests with fresh credentials

**Permissions**: `secrets: write`

### 2. Refresh Credentials (`refresh-cached-credentials.yml`)

**Trigger**: Manual only

**Purpose**: Update timestamp on existing credentials without full auth

**Steps**:
1. Load current credentials
2. Update timestamp to now
3. **Auto-update secret** with new timestamp
4. Upload artifact (backup)

**Permissions**: `secrets: write`

---

## Benefits

### ✅ Zero Manual Intervention
- No need to run commands locally
- No need to update secrets via GitHub UI
- Fully automated end-to-end

### ✅ Immediate Test Completion
- **Before**: Tests fail → wait 1 day → tests pass
- **After**: Tests fail → refresh credentials → tests pass (same run)

### ✅ Reduced Rate Limit Risk
- Auth tests run first and only when needed
- Remaining tests always use cached credentials
- Fewer auth API calls overall

### ✅ Clear Visibility
- Logs show when credentials are refreshed
- Logs show when secret is updated
- Artifacts uploaded for audit trail

---

## Log Examples

### Scenario 1: Cache Valid (No Refresh)

```
🔐 Running authentication tests to ensure credentials are fresh...
tests/integration/test_auth_flow.py::test_request_game_code SKIPPED [cached]
tests/integration/test_auth_flow.py::test_complete_auth_flow SKIPPED [cached]

Credentials cache exists - checking if it was updated during tests
Cache was not updated during this run

🧪 Running remaining integration tests with fresh credentials...
tests/integration/test_roster_live.py::test_get_roster PASSED ✓
tests/integration/test_roster_live.py::test_get_status PASSED ✓
```

### Scenario 2: Cache Expired (Auto-Refresh)

```
🔐 Running authentication tests to ensure credentials are fresh...
No valid cache found. Starting authentication flow...
Authentication attempt 1/3
Code request successful
Code received: 123456
Token exchange successful
Credentials cached for future tests

✓ Credentials were refreshed during this test run
📤 Automatically updating CACHED_CREDENTIALS secret...
✅ CACHED_CREDENTIALS secret updated successfully!
   Timestamp: 2026-01-28T12:34:56.789
   Email: REDACTED
   Server: en

🧪 Running remaining integration tests with fresh credentials...
tests/integration/test_roster_live.py::test_get_roster PASSED ✓
tests/integration/test_roster_live.py::test_get_status PASSED ✓
```

---

## Troubleshooting

### Secret Update Fails

If automatic update fails:
1. Check workflow logs for error details
2. Verify `secrets: write` permission is set
3. Check `CREDENTIALS_UPDATE_NEEDED.txt` artifact for manual instructions

**Manual fallback**:
```bash
# Download artifact
gh run download <RUN_ID> --name updated-credentials-cache

# Update secret
cat tests/integration/.credentials_cache.json | gh secret set CACHED_CREDENTIALS
```

### Auth Tests Fail

If auth tests fail but aren't rate limited:
- Check Mail.tm API availability
- Verify `TEST_ACCOUNT_EMAIL` and `TEST_ACCOUNT_EMAIL_PASSWORD` secrets
- Check Yostar API status
- Review circuit breaker logs for rate limit detection

### Rate Limit Detected

If circuit breaker triggers:
```
⚠️  RATE LIMIT DETECTED (error code 100302)
The Yostar API has rate limited email code requests.
Recommendation: Wait 1-2 hours before retrying, or use cached credentials.
```

**Solution**:
- Don't run auth tests again for 1-2 hours
- Use cached credentials (increase cache duration if needed)
- Consider increasing `CACHE_DURATION` from 1 day to 7 days

---

## Configuration

### Cache Duration

**Location**: `tests/integration/credential_cache.py:10`

```python
CACHE_DURATION = timedelta(days=1)  # Refresh credentials daily
```

**Options**:
- `days=1` - Daily refresh (current, more frequent auth)
- `days=7` - Weekly refresh (matches Yostar token validity, recommended)

### Workflow Schedule

**Location**: `.github/workflows/integration-tests-new.yml:7-8`

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

---

## Related Files

| File | Purpose |
|------|---------|
| `.github/workflows/integration-tests-new.yml` | Main integration test workflow with auto-update |
| `.github/workflows/refresh-cached-credentials.yml` | Manual refresh workflow with auto-update |
| `tests/integration/conftest.py` | Credential caching logic and circuit breaker |
| `tests/integration/credential_cache.py` | Cache save/load/validate functions |
| `tests/integration/test_auth_flow.py` | Auth tests that run first |
| `tests/integration/CIRCUIT_BREAKER.md` | Circuit breaker documentation |
| `tests/integration/README_CREDENTIALS.md` | General credential caching docs |

---

## Migration Notes

**Before this change**:
- All tests ran together
- Manual secret updates required
- Chicken-and-egg problem with expired credentials

**After this change**:
- Auth tests run first, then other tests
- Automatic secret updates
- Credentials refresh in same run, tests pass immediately

**No local changes needed** - existing tests work as-is, just run in different order.
