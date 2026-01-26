#!/bin/bash
# Script to download and update cached credentials from GitHub Actions artifacts

set -e

echo "📥 Downloading latest credentials from GitHub Actions..."

# Get the latest successful integration test run
RUN_ID=$(gh run list --workflow="integration-tests-new.yml" --status=success --limit=1 --json databaseId --jq '.[0].databaseId')

if [ -z "$RUN_ID" ]; then
    echo "❌ No successful integration test runs found"
    exit 1
fi

echo "Found run ID: $RUN_ID"

# Check if there's an updated credentials artifact
if gh run view "$RUN_ID" --json artifacts --jq '.artifacts[] | select(.name == "updated-credentials-cache")' > /dev/null 2>&1; then
    echo "✓ Credentials were updated in this run"

    # Download the artifact
    gh run download "$RUN_ID" --name updated-credentials-cache --dir /tmp/updated-creds

    if [ -f /tmp/updated-creds/.credentials_cache.json ]; then
        echo "📤 Updating CACHED_CREDENTIALS secret..."
        cat /tmp/updated-creds/.credentials_cache.json | gh secret set CACHED_CREDENTIALS
        echo "✅ Secret updated successfully!"

        # Show what was updated
        if [ -f /tmp/updated-creds/CREDENTIALS_UPDATE_NEEDED.txt ]; then
            echo ""
            cat /tmp/updated-creds/CREDENTIALS_UPDATE_NEEDED.txt
        fi

        # Cleanup
        rm -rf /tmp/updated-creds
    else
        echo "❌ Credentials file not found in artifact"
        exit 1
    fi
else
    echo "ℹ️  No credential updates needed - cache is still valid"
fi
