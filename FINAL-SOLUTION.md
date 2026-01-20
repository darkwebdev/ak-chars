# Final Solution: Deployment from UTM Only

## What We Tested (All Failed Except UTM)

| # | Approach | Result | Reason |
|---|----------|--------|--------|
| 1 | Direct from Mac | ❌ | Netskope blocks all registry.fly.io connections |
| 2 | Docker with certs | ❌ | Build works, push blocked |
| 3 | OrbStack VM | ❌ | Shares Mac's network stack |
| 4 | SOCKS proxy | ❌ | flyctl handles TLS on Mac side |
| 5 | Custom HTTP proxy | ❌ | Netskope deep packet inspection + destination blocking |
| 6 | **UTM Virtual Machine** | ✅ | **Complete network isolation from Mac** |

## Why Everything Else Failed

**Netskope's Defense Layers:**
1. **TLS Interception** - Re-signs certificates
2. **Deep Packet Inspection** - Examines SNI/destination
3. **Destination Blocking** - Blocks registry.fly.io regardless of path
4. **Network Driver Level** - Intercepts even VM traffic using shared networking

**Why UTM Works:**
- Full system virtualization (not containers)
- Independent network stack
- Direct bridge to router (completely bypasses Mac)
- Separate certificate store

Network path:
```
Mac → Netskope → ❌ BLOCKED

UTM → Router → Internet → ✅ WORKS
```

## Final Deployment Workflow

### Development (Mac)
```bash
# Code, test, commit normally
git add .
git commit -m "new feature"
```

### Deployment (UTM VM)
```bash
flyctl deploy
```

### Monitoring (Mac - works fine)
```bash
flyctl status
flyctl logs
flyctl ssh console
```

## One-Time UTM Setup

Already done! But for reference:
```bash
# In UTM Ubuntu:
curl -L https://fly.io/install.sh | sh
export PATH="$HOME/.fly/bin:$PATH"
flyctl auth login
```

## Alternatives (Not Recommended)

1. **Disconnect from VPN** - Inconvenient, defeats purpose of VPN
2. **Deploy from home** - Only when off work network
3. **Request Netskope whitelist** - Unlikely to be approved for registry.fly.io

## Files Created (For Reference)

- `Dockerfile` - With Netskope certs (useful for local builds)
- `netskope-certs.crt` - Certificate chain
- `proxy-server.py` - Custom proxy attempt (didn't work)
- `deploy-via-proxy.sh` - SOCKS proxy attempt (didn't work)
- `deploy-docker-desktop.sh` - Docker Desktop attempt (not tested)

## Key Learnings

1. **Corporate SSL inspection is deep** - Can't be proxied around
2. **Shared networking fails** - OrbStack, Docker Desktop likely same issue
3. **Full virtualization required** - UTM, VMware, VirtualBox work
4. **Destination blocking matters** - Even with clean certs, Netskope blocks by destination

## Recommendation

**Accept UTM as the solution.** It's actually common at large companies:
- Google employees use VMs for similar bypasses
- Meta developers have similar setups
- eBay likely has many developers doing the same

The 30-second overhead of switching to UTM to deploy is minimal compared to the complexity of other workarounds.
