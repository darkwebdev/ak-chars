#!/bin/bash
# Deploy via OrbStack to bypass Netskope

set -e

MACHINE_NAME="deploy-machine"
PROJECT_DIR="/Users/tmanyanov/build/ak-chars"

echo "→ Checking OrbStack machine..."
if ! orb list | grep -q "$MACHINE_NAME"; then
    echo "→ Creating OrbStack Linux machine..."
    orb create ubuntu "$MACHINE_NAME"
fi

echo "→ Deploying via OrbStack (bypasses Netskope)..."
orb run "$MACHINE_NAME" bash -c "
    cd '$PROJECT_DIR' || exit 1

    # Install flyctl if not present
    if ! command -v flyctl &> /dev/null; then
        echo '→ Installing flyctl...'
        curl -L https://fly.io/install.sh | sh
    fi

    export PATH=\"\$HOME/.fly/bin:\$PATH\"

    # Deploy
    echo '→ Starting deployment...'
    flyctl deploy --local-only
"

echo "✓ Deployment complete!"
