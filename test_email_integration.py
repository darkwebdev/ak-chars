#!/usr/bin/env python3
"""Quick integration test for email helper without requiring API server."""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'integration'))

from email_helper import MailTmClient, MailTmCodeFetcher

load_dotenv()

async def test_mail_tm_client():
    """Test Mail.tm client can login and fetch messages."""
    email = os.getenv("TEST_ACCOUNT_EMAIL")
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")

    print(f"Testing Mail.tm client with {email}")

    client = MailTmClient()
    try:
        # Test login
        print("1. Testing login...")
        token = await client.login(email, password)
        print(f"   ✓ Login successful! Token: {token[:30]}...")

        # Test get messages
        print("2. Testing get_messages...")
        messages = await client.get_messages(token)
        print(f"   ✓ Found {len(messages)} messages in inbox")

        # Test get full message if any exist
        if messages:
            print("3. Testing get_message (full message)...")
            first_msg = messages[0]
            full_msg = await client.get_message(token, first_msg["id"])
            print(f"   ✓ Retrieved message: {full_msg.get('subject', 'No subject')}")
            print(f"   From: {full_msg.get('from', {}).get('address', 'Unknown')}")

        # Test code fetcher initialization
        print("4. Testing MailTmCodeFetcher...")
        fetcher = MailTmCodeFetcher(client, token)
        print("   ✓ Code fetcher created successfully")

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await client.close()

if __name__ == "__main__":
    success = asyncio.run(test_mail_tm_client())
    exit(0 if success else 1)
