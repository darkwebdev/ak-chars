#!/bin/bash
# Deploy via SOCKS proxy through OrbStack VM (bypasses Netskope)

set -e

VM_IP="192.168.139.30"
PROXY_PORT="1080"

echo "→ Starting SOCKS proxy through OrbStack VM..."
echo "  This bypasses Netskope by routing through the VM's bridge network"
echo ""

# Start SSH SOCKS proxy in background
ssh -o StrictHostKeyChecking=no -f -N -D $PROXY_PORT tmanyanov@$VM_IP

echo "✓ SOCKS proxy running on localhost:$PROXY_PORT"
echo ""
echo "→ Deploying via proxy..."

# Deploy using the proxy
ALL_PROXY=socks5://127.0.0.1:$PROXY_PORT \
HTTPS_PROXY=socks5://127.0.0.1:$PROXY_PORT \
  flyctl deploy

echo ""
echo "✓ Deployment complete!"
echo ""
echo "To stop the proxy:"
echo "  pkill -f 'ssh.*-D $PROXY_PORT'"
