#!/usr/bin/env python3
"""Comprehensive readiness check for integration tests."""

import os
import sys
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'integration'))
from email_helper import MailTmClient


async def check_mail_tm_account():
    """Check if Mail.tm account is accessible."""
    print(f"\n{BLUE}[1/6] Checking Mail.tm Account...{RESET}")

    email = os.getenv("TEST_ACCOUNT_EMAIL")
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")

    if not email or not password:
        print(f"  {RED}✗ Credentials not found in .env{RESET}")
        return False

    print(f"  Email: {email}")

    client = MailTmClient()
    try:
        token = await client.login(email, password)
        print(f"  {GREEN}✓ Login successful{RESET}")

        messages = await client.get_messages(token)
        print(f"  {GREEN}✓ Can access inbox ({len(messages)} messages){RESET}")

        await client.close()
        return True
    except Exception as e:
        print(f"  {RED}✗ Failed: {e}{RESET}")
        await client.close()
        return False


def check_environment_variables():
    """Check if all required environment variables are set."""
    print(f"\n{BLUE}[2/6] Checking Environment Variables...{RESET}")

    required_vars = [
        "TEST_ACCOUNT_EMAIL",
        "TEST_ACCOUNT_EMAIL_PASSWORD",
        "TEST_ACCOUNT_SERVER",
    ]

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password
            display_value = value if "PASSWORD" not in var else "*" * len(value)
            print(f"  {GREEN}✓{RESET} {var} = {display_value}")
        else:
            print(f"  {RED}✗{RESET} {var} not set")
            all_set = False

    return all_set


async def check_api_server():
    """Check if API server is running."""
    print(f"\n{BLUE}[3/6] Checking API Server...{RESET}")

    api_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to get OpenAPI docs
            response = await client.get(f"{api_url}/openapi.json")
            if response.status_code == 200:
                data = response.json()
                print(f"  {GREEN}✓ Server running at {api_url}{RESET}")
                print(f"  {GREEN}✓ API: {data.get('info', {}).get('title', 'Unknown')}{RESET}")
                return True
            else:
                print(f"  {RED}✗ Server returned status {response.status_code}{RESET}")
                return False
    except httpx.ConnectError:
        print(f"  {RED}✗ Server not running at {api_url}{RESET}")
        print(f"  {YELLOW}  → Start with: python3 start_test_server.py{RESET}")
        return False
    except Exception as e:
        print(f"  {RED}✗ Error: {e}{RESET}")
        return False


def check_dependencies():
    """Check if all Python dependencies are installed."""
    print(f"\n{BLUE}[4/6] Checking Python Dependencies...{RESET}")

    required_packages = [
        "pytest",
        "pytest_asyncio",
        "pytest_timeout",
        "httpx",
        "fastapi",
        "uvicorn",
        "arkprts",
        "strawberry",
        "dotenv"  # python-dotenv imports as 'dotenv'
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  {GREEN}✓{RESET} {package}")
        except ImportError:
            print(f"  {RED}✗{RESET} {package} not installed")
            all_installed = False

    if not all_installed:
        print(f"\n  {YELLOW}→ Install with: pip install -r server/requirements.txt{RESET}")

    return all_installed


def check_test_files():
    """Check if all test files exist."""
    print(f"\n{BLUE}[5/6] Checking Test Files...{RESET}")

    required_files = [
        "tests/integration/__init__.py",
        "tests/integration/conftest.py",
        "tests/integration/email_helper.py",
        "tests/integration/test_auth_flow.py",
        "tests/integration/test_roster_live.py",
        "pytest.ini",
        ".env"
    ]

    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"  {GREEN}✓{RESET} {file_path} ({size} bytes)")
        else:
            print(f"  {RED}✗{RESET} {file_path} missing")
            all_exist = False

    return all_exist


async def check_game_account():
    """Check if game account is set up (by attempting auth)."""
    print(f"\n{BLUE}[6/6] Checking Game Account Status...{RESET}")

    print(f"  {YELLOW}⚠ Game account setup cannot be verified automatically{RESET}")
    print(f"  {YELLOW}⚠ You must create an Arknights account manually{RESET}")
    print(f"\n  Steps to create account:")
    print(f"    1. Download Arknights (EN server)")
    print(f"    2. Choose 'Email Registration'")
    print(f"    3. Use email: {os.getenv('TEST_ACCOUNT_EMAIL')}")
    print(f"    4. Check Mail.tm inbox for verification code")
    print(f"    5. Complete in-game tutorial")

    # Check if we can at least request a code
    api_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{api_url}/auth/game-code",
                json={
                    "email": os.getenv("TEST_ACCOUNT_EMAIL"),
                    "server": os.getenv("TEST_ACCOUNT_SERVER", "en")
                }
            )
            if response.status_code == 200:
                print(f"\n  {GREEN}✓ Auth endpoint is working (code can be requested){RESET}")
                return True
            else:
                print(f"\n  {YELLOW}⚠ Auth endpoint returned {response.status_code}{RESET}")
                return False
    except Exception as e:
        print(f"\n  {RED}✗ Cannot check auth endpoint: {e}{RESET}")
        return False


async def main():
    """Run all readiness checks."""
    print(f"\n{'='*70}")
    print(f"  {BLUE}Integration Tests - Readiness Check{RESET}")
    print(f"{'='*70}")

    checks = [
        ("Mail.tm Account", await check_mail_tm_account()),
        ("Environment Variables", check_environment_variables()),
        ("API Server", await check_api_server()),
        ("Python Dependencies", check_dependencies()),
        ("Test Files", check_test_files()),
        ("Game Account", await check_game_account())
    ]

    print(f"\n{'='*70}")
    print(f"  {BLUE}Summary{RESET}")
    print(f"{'='*70}\n")

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for name, result in checks:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {status}  {name}")

    print(f"\n{'='*70}")

    if passed == total:
        print(f"  {GREEN}✓ ALL CHECKS PASSED - Ready to run tests!{RESET}")
        print(f"\n  Run tests with: pytest tests/integration/ -v -m integration")
    elif passed >= total - 1 and not checks[5][1]:  # All pass except game account
        print(f"  {YELLOW}⚠ ALMOST READY - Create game account to complete setup{RESET}")
        print(f"\n  You can run validation tests now:")
        print(f"    pytest tests/integration/ -v -k 'invalid or request_game'")
    else:
        print(f"  {RED}✗ {total - passed} CHECK(S) FAILED - Fix issues above{RESET}")

    print(f"{'='*70}\n")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interrupted by user{RESET}")
        sys.exit(1)
