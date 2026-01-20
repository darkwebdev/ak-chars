# Deployment Summary: Netskope Bypass Attempts

## What We Tried

### 1. ✅ Certificate Trust in Docker (Partial Success)
- Added Netskope/eBay certificates to Dockerfile
- **Result**: pip install works, but push to Fly.io still blocked

### 2. ❌ OrbStack Linux VM
- Attempted to deploy from OrbStack VM
- **Result**: Failed - inherits Mac's certificate store

### 3. ❌ SOCKS Proxy through VM
- Set up SSH tunnel through OrbStack bridge network
- **Result**: Failed - flyctl still encounters certificate errors

### 4. ✅ UTM Virtual Machine (Works!)
- Full virtualization with independent network stack
- **Result**: Complete bypass of Netskope

## Why Each Approach Worked or Failed

| Method | Network Path | Certificate Store | Result |
|--------|--------------|-------------------|--------|
| Mac directly | Mac → Netskope → Internet | Mac (Netskope certs) | ❌ Blocked |
| OrbStack VM | Mac → Netskope → Internet | Mac (shared) | ❌ Blocked |
| SOCKS proxy | Mac → VM → Internet | Mac (flyctl uses Mac's) | ❌ Blocked |
| UTM VM | VM → Router → Internet | VM (independent) | ✅ Works |

## Recommended Solution

**Deploy from UTM VM** - it's the only reliable way to bypass Netskope.

### One-Time Setup
```bash
# In UTM:
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"
flyctl auth login
```

### Every Deployment
```bash
# In UTM:
cd ~/ak-chars  # or your mounted project path
flyctl deploy
```

## Why UTM Works

UTM provides **full system virtualization**:
- Independent network stack
- Separate certificate store
- Direct bridge to your router (bypasses Mac's VPN)

Network flow:
```
Mac (Netskope blocks)
  ❌

UTM VM → Router → Internet
  ✅
```

## Lessons Learned

1. **OrbStack** is great for development but shares too much with the host OS
2. **SOCKS proxies** don't help when the client (flyctl) has certificate issues
3. **Full virtualization** (UTM, VirtualBox, VMware) is needed for corporate network bypass
4. **Certificate interception** at the TLS layer can't be proxied around

## Files Created

- `Dockerfile` - With Netskope certificate trust (helps with local builds)
- `netskope-certs.crt` - Combined certificate chain
- `deploy-via-proxy.sh` - SOCKS proxy attempt (doesn't work, kept for reference)
- `README-DEPLOY.md` - Deployment instructions

## Future Options

If you need Mac-native deployment in the future:
- Use eBay's internal deployment tools (if available)
- Request Netskope whitelist for registry.fly.io
- Deploy when off VPN (disconnect temporarily)
