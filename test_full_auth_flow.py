#!/usr/bin/env python3
"""
Test the complete authentication flow end-to-end.

This script simulates what happens in test_complete_auth_flow:
1. Request verification code
2. Poll email for code
3. Exchange code for game token
4. Verify token works

Run this after creating the Arknights game account.
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'integration'))

from email_helper import MailTmClient, MailTmCodeFetcher

load_dotenv()

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


async def test_full_flow():
    """Test the complete authentication flow."""
    print(f"\n{'='*70}")
    print(f"  {BLUE}Full Authentication Flow Test{RESET}")
    print(f"{'='*70}\n")

    email = os.getenv("TEST_ACCOUNT_EMAIL")
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")
    server = os.getenv("TEST_ACCOUNT_SERVER", "en")
    api_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    print(f"Email: {email}")
    print(f"Server: {server}")
    print(f"API: {api_url}\n")

    # Step 1: Login to Mail.tm
    print(f"{BLUE}[1/5] Logging into Mail.tm...{RESET}")
    mail_client = MailTmClient()
    try:
        mail_token = await mail_client.login(email, password)
        print(f"  {GREEN}✓ Login successful{RESET}")
    except Exception as e:
        print(f"  {RED}✗ Failed: {e}{RESET}")
        await mail_client.close()
        return False

    # Step 2: Request game code
    print(f"\n{BLUE}[2/5] Requesting verification code from Arknights...{RESET}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_url}/auth/game-code",
                json={"email": email, "server": server}
            )

            if response.status_code == 200:
                data = response.json()
                print(f"  {GREEN}✓ Code requested successfully{RESET}")
                print(f"  Response: {data}")
            else:
                print(f"  {RED}✗ Failed with status {response.status_code}{RESET}")
                print(f"  Response: {response.text}")
                await mail_client.close()
                return False
    except Exception as e:
        print(f"  {RED}✗ Error: {e}{RESET}")
        await mail_client.close()
        return False

    # Step 3: Wait for email and extract code
    print(f"\n{BLUE}[3/5] Waiting for verification email...{RESET}")
    print(f"  {YELLOW}⏱  This may take 30-90 seconds...{RESET}")

    fetcher = MailTmCodeFetcher(mail_client, mail_token)
    try:
        start_time = datetime.now()
        code = await fetcher.wait_for_code(timeout=120, poll_interval=5)
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"  {GREEN}✓ Code received: {code}{RESET}")
        print(f"  ⏱  Wait time: {elapsed:.1f} seconds")
    except TimeoutError:
        print(f"  {RED}✗ Timeout: No code received within 120 seconds{RESET}")
        print(f"  {YELLOW}  This might mean:{RESET}")
        print(f"     - Game account doesn't exist yet")
        print(f"     - Email was sent to different address")
        print(f"     - Yostar servers are slow")
        await mail_client.close()
        return False
    except Exception as e:
        print(f"  {RED}✗ Error: {e}{RESET}")
        await mail_client.close()
        return False

    # Step 4: Exchange code for game token
    print(f"\n{BLUE}[4/5] Exchanging code for game token...{RESET}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_url}/auth/game-token",
                json={
                    "email": email,
                    "code": code,
                    "server": server
                }
            )

            if response.status_code == 200:
                credentials = response.json()
                print(f"  {GREEN}✓ Token exchange successful{RESET}")
                print(f"  Channel UID: {credentials.get('channel_uid', 'N/A')[:20]}...")
                print(f"  Yostar Token: {credentials.get('yostar_token', 'N/A')[:20]}...")

                # Save credentials to cache for pytest to use
                sys.path.insert(0, 'tests/integration')
                from credential_cache import save_credentials
                save_credentials(
                    {"channel_uid": credentials["channel_uid"], "yostar_token": credentials["yostar_token"]},
                    email,
                    server
                )
                print(f"  {GREEN}✓ Credentials cached for pytest tests{RESET}")
            else:
                print(f"  {RED}✗ Failed with status {response.status_code}{RESET}")
                print(f"  Response: {response.text}")
                await mail_client.close()
                return False
    except Exception as e:
        print(f"  {RED}✗ Error: {e}{RESET}")
        await mail_client.close()
        return False

    # Step 5: Test credentials with roster API
    print(f"\n{BLUE}[5/5] Testing credentials with roster API...{RESET}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{api_url}/my/roster",
                json={
                    "channel_uid": credentials["channel_uid"],
                    "yostar_token": credentials["yostar_token"],
                    "server": server
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    chars = data.get("chars", {})
                    print(f"  {GREEN}✓ Credentials work!{RESET}")
                    print(f"  {GREEN}✓ Retrieved {len(chars)} operators{RESET}")

                    if chars:
                        # Show sample operator
                        first_char = next(iter(chars.values()))
                        print(f"\n  Sample operator:")
                        print(f"    ID: {first_char.get('charId')}")
                        print(f"    Level: {first_char.get('level')}")
                        print(f"    Elite: {first_char.get('evolvePhase', 0)}")
                else:
                    print(f"  {YELLOW}⚠ Response received but ok=false{RESET}")
                    print(f"  Data: {data}")
            else:
                print(f"  {RED}✗ Failed with status {response.status_code}{RESET}")
                print(f"  Response: {response.text[:200]}")
                await mail_client.close()
                return False
    except Exception as e:
        print(f"  {RED}✗ Error: {e}{RESET}")
        await mail_client.close()
        return False

    await mail_client.close()

    print(f"\n{'='*70}")
    print(f"  {GREEN}✓ ALL STEPS PASSED - Authentication flow working!{RESET}")
    print(f"{'='*70}\n")

    print(f"{GREEN}Next steps:{RESET}")
    print(f"  1. Run full integration test suite:")
    print(f"     pytest tests/integration/ -v -m integration")
    print(f"  2. Configure GitHub Secrets for CI")
    print(f"  3. Test CI workflow\n")

    return True


if __name__ == "__main__":
    print(f"\n{YELLOW}WARNING: This test requires an active Arknights game account{RESET}")
    print(f"{YELLOW}         using email: {os.getenv('TEST_ACCOUNT_EMAIL')}{RESET}\n")

    try:
        success = asyncio.run(test_full_flow())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interrupted by user{RESET}")
        sys.exit(1)
