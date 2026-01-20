#!/bin/bash
# Start HTTP/HTTPS proxy in OrbStack VM

set -e

VM_NAME="deploy-machine"
VM_IP="192.168.139.30"
PROXY_PORT="8888"

echo "→ Copying proxy server to VM..."
orb -m "$VM_NAME" mkdir -p /tmp/proxy
cat proxy-server.py | orb -m "$VM_NAME" tee /tmp/proxy/proxy-server.py > /dev/null
orb -m "$VM_NAME" chmod +x /tmp/proxy/proxy-server.py

echo "→ Starting proxy server in VM..."
echo "  VM IP: $VM_IP"
echo "  Port: $PROXY_PORT"
echo ""

# Start proxy in background and show output
orb -m "$VM_NAME" python3 /tmp/proxy/proxy-server.py &
PROXY_PID=$!

echo "✓ Proxy started (PID: $PROXY_PID)"
echo ""
echo "To deploy using this proxy:"
echo "  export HTTP_PROXY=http://$VM_IP:$PROXY_PORT"
echo "  export HTTPS_PROXY=http://$VM_IP:$PROXY_PORT"
echo "  flyctl deploy"
echo ""
echo "To stop proxy:"
echo "  kill $PROXY_PID"
echo "  orb -m $VM_NAME pkill -f proxy-server.py"
