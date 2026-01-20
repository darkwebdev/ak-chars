# Fly.io Deployment Guide

## Quick Deploy

```bash
./deploy.sh
```

The script will guide you through the entire process.

---

## Manual Deployment

If you prefer to run commands manually:

### 1. Install Fly CLI

```bash
brew install flyctl
```

### 2. Login to Fly.io

```bash
flyctl auth signup  # or: flyctl auth login
```

### 3. Create the app

```bash
flyctl launch --no-deploy
```

This will:
- Ask you to choose a region (pick one close to you)
- Create the app on Fly.io
- Update `fly.toml` with your app name

### 4. Set environment variables

```bash
# Required
flyctl secrets set JWT_SECRET=0b1dd73601787df8dd1a6c6c8e9007bbf9d1251afab9910d771ed61908896446
flyctl secrets set USE_FIXTURES=false

# Required if you have a frontend
flyctl secrets set CORS_ORIGIN=https://your-frontend.vercel.app

# Optional - only if you want email functionality
flyctl secrets set SMTP_HOST=smtp.gmail.com
flyctl secrets set SMTP_PORT=587
flyctl secrets set SMTP_USER=your-email@gmail.com
flyctl secrets set SMTP_PASS=your-app-password
```

### 5. Deploy

```bash
flyctl deploy
```

### 6. Check status

```bash
flyctl status
flyctl logs
```

Your API will be live at: `https://your-app-name.fly.dev`

---

## Environment Variables

### Required

- **JWT_SECRET**: `0b1dd73601787df8dd1a6c6c8e9007bbf9d1251afab9910d771ed61908896446`
  - Used for signing JWT tokens
  - Already generated for you (keep it secret!)

- **USE_FIXTURES**: `false`
  - Set to `true` for development (uses fixture data)
  - Set to `false` for production (uses live game API)

### Optional

- **CORS_ORIGIN**: Your frontend URL (e.g., `https://your-app.vercel.app`)
  - Allows your frontend to make API requests
  - Can be set later if you don't have a frontend yet

- **SMTP_HOST**: SMTP server hostname (e.g., `smtp.gmail.com`)
- **SMTP_PORT**: SMTP server port (e.g., `587`)
- **SMTP_USER**: Your email address
- **SMTP_PASS**: Your email app password
  - Only needed if you want email functionality
  - Without SMTP, emails will be logged instead

---

## Useful Commands

```bash
# View logs in real-time
flyctl logs

# Check app status and resource usage
flyctl status

# SSH into your VM
flyctl ssh console

# List environment variables (values are hidden)
flyctl secrets list

# Update an environment variable
flyctl secrets set VARIABLE_NAME=new-value

# Restart the app
flyctl apps restart

# Scale to multiple instances (costs money)
flyctl scale count 2

# View your app in the browser
flyctl open
```

---

## Testing Your Deployment

Once deployed, test your API:

```bash
# Health check
curl https://your-app-name.fly.dev

# Test a specific endpoint
curl https://your-app-name.fly.dev/graphql

# GraphiQL interface (in browser)
open https://your-app-name.fly.dev/graphql
```

---

## Troubleshooting

### App won't start
```bash
flyctl logs  # Check for errors
```

### Need to redeploy
```bash
flyctl deploy
```

### Want to destroy and start over
```bash
flyctl apps destroy your-app-name
./deploy.sh  # Start fresh
```

### Cold starts happening (app sleeping)
Check your `fly.toml`:
```toml
auto_stop_machines = false
auto_start_machines = false
min_machines_running = 1
```

These settings prevent your app from sleeping.

---

## Cost Estimate

With the free tier settings in `fly.toml`:
- **1 VM**: 256MB RAM, shared CPU
- **Always running**: No cold starts
- **Free tier**: Should stay within limits

If you exceed free tier:
- ~$2-5/month for a single always-on VM
- Check usage: `flyctl dashboard`
