#!/usr/bin/env python3
"""Quick script to verify Mail.tm credentials work."""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_mail_tm():
    email = os.getenv("TEST_ACCOUNT_EMAIL")
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")

    print(f"Testing Mail.tm login for: {email}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.mail.tm/token",
                json={"address": email, "password": password},
                timeout=30.0
            )
            response.raise_for_status()
            token = response.json()["token"]
            print(f"✓ Login successful! Token: {token[:20]}...")

            # Try to fetch messages
            response = await client.get(
                "https://api.mail.tm/messages",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            messages = response.json()
            message_count = len(messages.get("hydra:member", []))
            print(f"✓ Can access mailbox. Found {message_count} messages.")

            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(verify_mail_tm())
    exit(0 if success else 1)
