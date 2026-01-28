"""Credential caching to avoid Yostar rate limits."""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta


CACHE_FILE = Path(__file__).parent / ".credentials_cache.json"
CACHE_DURATION = timedelta(days=1)  # Refresh credentials daily to ensure freshness
RETRY_COOLDOWN = timedelta(hours=2)  # Wait 2 hours before retrying after failed refresh


def save_credentials(credentials: dict, email: str, server: str):
    """Save credentials to cache file."""
    cache_data = {
        "credentials": credentials,
        "email": email,
        "server": server,
        "timestamp": datetime.now().isoformat()
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(cache_data, f)


def mark_refresh_attempt(email: str, server: str, failed: bool = False):
    """Mark that we attempted to refresh credentials.

    This prevents retry storms when rate limited. If a refresh attempt fails,
    we record the attempt time and won't try again for RETRY_COOLDOWN hours.

    Args:
        email: Email address
        server: Server code
        failed: Whether the refresh attempt failed
    """
    if not CACHE_FILE.exists():
        return

    try:
        with open(CACHE_FILE, "r") as f:
            cache_data = json.load(f)

        if failed:
            cache_data["last_failed_refresh"] = datetime.now().isoformat()
        else:
            cache_data["last_refresh_attempt"] = datetime.now().isoformat()
            # Clear failed refresh marker on success
            cache_data.pop("last_failed_refresh", None)

        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f)
    except Exception:
        pass


def should_attempt_refresh(email: str, server: str) -> bool:
    """Check if we should attempt to refresh credentials.

    Returns False if:
    - We have valid (non-expired) credentials
    - We recently failed to refresh (within RETRY_COOLDOWN)

    This prevents rate limit retry storms.
    """
    if not CACHE_FILE.exists():
        return True

    try:
        with open(CACHE_FILE, "r") as f:
            cache_data = json.load(f)

        # Check if cache is for same email/server
        if cache_data.get("email") != email or cache_data.get("server") != server:
            return True

        # If we have valid credentials, don't refresh
        timestamp = datetime.fromisoformat(cache_data["timestamp"])
        if datetime.now() - timestamp <= CACHE_DURATION:
            return False

        # If we recently failed to refresh, don't retry yet
        if "last_failed_refresh" in cache_data:
            last_failed = datetime.fromisoformat(cache_data["last_failed_refresh"])
            if datetime.now() - last_failed < RETRY_COOLDOWN:
                return False

        return True
    except Exception:
        return True


def load_credentials(email: str, server: str, allow_expired: bool = False) -> dict | None:
    """Load credentials from cache if valid.

    Args:
        email: Email address to match
        server: Server code to match
        allow_expired: If True, return expired credentials instead of None.
                      Useful when rate limited and can't refresh.

    Returns:
        Credentials dict if found, None otherwise
    """
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE, "r") as f:
            cache_data = json.load(f)

        # Check if cache is for same email/server
        if cache_data.get("email") != email or cache_data.get("server") != server:
            return None

        # Check if cache is still valid (within 1 day)
        timestamp = datetime.fromisoformat(cache_data["timestamp"])
        if datetime.now() - timestamp > CACHE_DURATION:
            # Return expired credentials if allowed (e.g., when rate limited)
            if allow_expired:
                return cache_data.get("credentials")
            return None

        return cache_data.get("credentials")
    except Exception:
        return None


def clear_cache():
    """Clear credentials cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
