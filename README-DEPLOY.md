# Deployment Guide (eBay/Netskope Network)

## Why Deployment Fails from Mac

Netskope intercepts HTTPS traffic with self-signed certificates:
- ✅ Building locally works (we added Netskope certs to Dockerfile)
- ❌ Pushing to Fly.io fails (Netskope blocks the connection)
- ❌ Remote builder fails (TLS certificate errors)

## Solution: Deploy from UTM/VM

### One-Time Setup in UTM

```bash
# 1. Inside your UTM VM:
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"

# 2. Login to Fly.io
flyctl auth login
# This will open a browser - complete the login

# 3. Clone/copy your project to the VM, or mount Mac directory
```

### Deploy from UTM

```bash
cd /path/to/ak-chars
flyctl deploy
```

**That's it!** UTM bypasses Netskope because it uses bridged networking.

## Quick Deploy Script

On your Mac, create this script to remind you:

```bash
#!/bin/bash
echo "📦 To deploy:"
echo ""
echo "1. Open UTM VM"
echo "2. Run: cd ~/ak-chars"  # or wherever you mounted the project
echo "3. Run: flyctl deploy"
echo ""
echo "✓ Deploy completes in ~2-3 minutes"
```

## Future Deploys

After code changes on your Mac:
1. Commit changes (UTM will see them if using shared folder)
2. SSH into UTM
3. Run `flyctl deploy`

## Alternative: Home Network

You can also deploy when disconnected from eBay VPN:
```bash
# Disconnect from VPN
flyctl deploy --local-only
# Reconnect to VPN
```

## Monitoring

These work from your Mac (not blocked by Netskope):
```bash
flyctl status
flyctl logs
flyctl ssh console
```
