"""Credential caching to avoid Yostar rate limits."""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta


CACHE_FILE = Path(__file__).parent / ".credentials_cache.json"
CACHE_DURATION = timedelta(days=1)  # Credentials valid for 1 day


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


def load_credentials(email: str, server: str) -> dict | None:
    """Load credentials from cache if valid."""
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
            return None

        return cache_data.get("credentials")
    except Exception:
        return None


def clear_cache():
    """Clear credentials cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
