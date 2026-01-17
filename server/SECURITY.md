# Security Guidelines

## Sensitive Data Protection

This project handles sensitive authentication credentials including:

- `yostar_token` - Game authentication tokens
- `channel_uid` - User channel identifiers
- `code` - Email verification codes
- SMTP credentials (username/password)
- JWT secrets

### Implemented Protections

#### 1. Environment Variables

All sensitive configuration is stored in `.env` files:

- `.env` is in `.gitignore` and never committed
- `.env.example` provides a template with placeholder values
- Use `python-dotenv` to load environment variables

#### 2. Log Sanitization

The `main.py` middleware automatically sanitizes logs:

- Redacts sensitive fields from request/response bodies
- Masks authorization headers
- Prevents credential leakage in application logs

Fields automatically redacted:

- `yostar_token`, `token`, `channel_uid`, `channelUid`
- `password`, `secret`, `api_key`, `apiKey`
- `code`, `authorization`, `auth`

#### 3. Secure Logging Practices

- Channel UIDs are truncated to first 8 chars in logs
- Full tokens are never logged
- Email addresses are logged for audit purposes only

### Developer Guidelines

#### DO:

✅ Use environment variables for all secrets
✅ Test with `.env.example` template
✅ Add new sensitive fields to the sanitization list in `main.py`
✅ Use HTTPS in production
✅ Rotate JWT secrets regularly

#### DON'T:

❌ Hardcode credentials in source files
❌ Log full tokens or passwords
❌ Commit `.env` files to version control
❌ Share credentials in issue trackers or chat
❌ Expose credentials in error messages returned to clients

### Client-Side Security

When consuming the API:

- Store credentials securely (encrypted storage, not localStorage)
- Never log or display full tokens
- Use HTTPS for all API calls
- Implement token refresh/rotation
- Clear credentials on logout

### Testing Securely

For testing:

1. Copy `.env.example` to `.env`
2. Fill in test credentials (use test accounts only)
3. Never commit your `.env` file
4. Use mock/stub services when possible

### Incident Response

If credentials are accidentally exposed:

1. Immediately rotate all affected secrets
2. Revoke compromised tokens
3. Review logs for unauthorized access
4. Update `.gitignore` if needed
5. Consider using tools like `git-secrets` or `truffleHog`

### Additional Tools

Consider adding:

- `pre-commit` hooks to scan for secrets
- Secret scanning in CI/CD pipeline
- Vault or secret management service for production
