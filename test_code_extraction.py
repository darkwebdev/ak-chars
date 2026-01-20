#!/usr/bin/env python3
"""Test code extraction from the existing email."""

import asyncio
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'integration'))

from email_helper import MailTmClient, MailTmCodeFetcher

load_dotenv()

async def test_code_extraction():
    """Test extracting verification code from existing email."""
    email = os.getenv("TEST_ACCOUNT_EMAIL")
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")

    print(f"Testing code extraction for {email}")

    client = MailTmClient()
    try:
        # Login
        token = await client.login(email, password)
        messages = await client.get_messages(token)

        if not messages:
            print("❌ No messages in inbox to test with")
            return False

        # Get first message
        first_msg = messages[0]
        full_msg = await client.get_message(token, first_msg["id"])

        print(f"\nMessage subject: {full_msg.get('subject')}")
        print(f"From: {full_msg.get('from', {}).get('address')}")

        # Try to extract code
        fetcher = MailTmCodeFetcher(client, token)
        text_body = full_msg.get("text", "")
        html_body = full_msg.get("html", [""])[0] if full_msg.get("html") else ""

        code = fetcher._extract_code_from_body(text_body or html_body)

        if code:
            print(f"\n✅ Successfully extracted code: {code}")
            print(f"   Code length: {len(code)}")
            print(f"   Is all digits: {code.isdigit()}")
            return True
        else:
            print("\n❌ Failed to extract code")
            print(f"Text body preview: {text_body[:200]}")
            return False

    finally:
        await client.close()

if __name__ == "__main__":
    success = asyncio.run(test_code_extraction())
    exit(0 if success else 1)
