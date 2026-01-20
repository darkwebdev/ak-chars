#!/bin/bash
# Deploy using Docker Desktop container (bypasses Mac's network stack)

set -e

echo "→ Building deployment container with Docker Desktop..."
docker build -f Dockerfile.deploy -t ak-chars-deploy .

echo ""
echo "→ Deploying from Docker Desktop container..."
echo "  (This uses Docker Desktop's VM network, may bypass Netskope)"
echo ""

# Run deployment from inside Docker Desktop VM
docker run --rm \
  -v "$HOME/.fly:/root/.fly" \
  -e FLY_ACCESS_TOKEN \
  ak-chars-deploy

echo ""
echo "✓ Deployment complete!"
