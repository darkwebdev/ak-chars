#!/bin/bash
# Script to refresh CACHED_CREDENTIALS GitHub secret with updated timestamp
set -e

echo "=== Refreshing CACHED_CREDENTIALS Secret ===" >&2
echo "" >&2

# Fetch and update the secret
gh secret set CACHED_CREDENTIALS --body "$(
  gh api /repos/{owner}/{repo}/actions/secrets/CACHED_CREDENTIALS 2>/dev/null || echo '{}'
)" --app actions || {
  echo "ERROR: Cannot read current secret value" >&2
  echo "" >&2
  echo "Creating fresh template..." >&2

  # Generate template with current timestamp
  python3 << 'EOF'
import json
from datetime import datetime

template = {
    "credentials": {
        "channel_uid": "YOUR_CHANNEL_UID_HERE",
        "yostar_token": "YOUR_YOSTAR_TOKEN_HERE"
    },
    "email": "YOUR_TEST_EMAIL_HERE",
    "server": "en",
    "timestamp": datetime.now().isoformat()
}

print(json.dumps(template, indent=2))
EOF

  echo "" >&2
  echo "Please update the placeholders with real values and run:" >&2
  echo "  cat /path/to/updated.json | gh secret set CACHED_CREDENTIALS" >&2
  exit 1
}

echo "✅ Secret refreshed successfully" >&2
