# Security Policy

## Secrets Management

This repository follows security best practices:

### ✅ What's Protected

- **API Tokens**: Stored in GitHub Secrets (encrypted)
- **JWT Secrets**: Set via Fly.io environment variables
- **SMTP Credentials**: Never committed to git
- **Private Keys**: Listed in `.gitignore`

### 🔒 Environment Variables

Required secrets (set in Fly.io):
- `JWT_SECRET` - JWT signing key
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` - Email configuration
- `USE_FIXTURES` - Development mode flag

**Never commit `.env` files!** Only `.env.example` should be in version control.

### 📋 Local Development

1. Copy `.env.example` to `.env`
2. Fill in your local values
3. Never commit `.env` to git

### 🚨 What NOT to Commit

- `.env` files
- API keys or tokens
- Certificates (`.crt`, `.pem`, `.key`)
- Private keys
- Database credentials
- Internal network configurations

### 📢 Reporting Security Issues

If you discover a security vulnerability, please email the repository owner directly rather than creating a public issue.

## Deployment Security

- GitHub Actions uses encrypted secrets for Fly.io token
- Fly.io secrets are never exposed in logs or code
- All HTTPS connections use proper TLS
- CORS is configured to restrict origins

## Code Security

- Input validation on all API endpoints
- Sensitive data sanitization in logs (see `server/main.py`)
- JWT token expiration enforced
- Email validation for authentication

## Dependencies

Keep dependencies updated:
```bash
# Python dependencies
pip list --outdated

# Node dependencies
yarn outdated
```
