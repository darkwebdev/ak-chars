"""pytest configuration and fixtures for integration tests."""

import os
import pytest
import httpx
import logging
from typing import Optional
from dotenv import load_dotenv
from .email_helper import MailTmClient, MailTmCodeFetcher
from .credential_cache import save_credentials, load_credentials

# Load environment variables from .env file
load_dotenv()

# Configure logging for integration tests
logger = logging.getLogger("integration_tests")


def pytest_configure(config):
    """Register custom markers and configure logging."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring live credentials"
    )

    # Enable verbose logging if -v flag is used
    if config.getoption("verbose") > 0:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.setLevel(logging.DEBUG)


def _skip_if_no_credentials():
    """Skip tests if credentials not configured."""
    if not os.getenv("TEST_ACCOUNT_EMAIL"):
        pytest.skip("Integration tests require TEST_ACCOUNT_EMAIL environment variable")


@pytest.fixture(scope="session")
def test_email() -> str:
    """Get test account email from environment.

    Returns:
        Test account email address

    Raises:
        pytest.skip: If TEST_ACCOUNT_EMAIL not set
    """
    _skip_if_no_credentials()
    return os.getenv("TEST_ACCOUNT_EMAIL")


@pytest.fixture(scope="session")
def test_email_password() -> str:
    """Get test account email password from environment.

    Returns:
        Test account email password

    Raises:
        pytest.skip: If TEST_ACCOUNT_EMAIL_PASSWORD not set
    """
    _skip_if_no_credentials()
    password = os.getenv("TEST_ACCOUNT_EMAIL_PASSWORD")
    if not password:
        pytest.skip("Integration tests require TEST_ACCOUNT_EMAIL_PASSWORD environment variable")
    return password


@pytest.fixture(scope="session")
def test_server() -> str:
    """Get test server from environment.

    Returns:
        Server code (default: 'en')
    """
    return os.getenv("TEST_ACCOUNT_SERVER", "en")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Get API base URL from environment.

    Returns:
        API base URL (default: http://127.0.0.1:8000)
    """
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
async def mail_tm_client():
    """Create Mail.tm API client.

    Yields:
        MailTmClient instance
    """
    client = MailTmClient()
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def mail_tm_token(mail_tm_client, test_email, test_email_password) -> str:
    """Login to Mail.tm and get JWT token.

    Args:
        mail_tm_client: MailTmClient fixture
        test_email: Test email fixture
        test_email_password: Test email password fixture

    Returns:
        JWT token for Mail.tm API
    """
    token = await mail_tm_client.login(test_email, test_email_password)
    return token


@pytest.fixture
async def email_fetcher(mail_tm_client, mail_tm_token):
    """Create email code fetcher.

    Args:
        mail_tm_client: MailTmClient fixture
        mail_tm_token: JWT token fixture

    Yields:
        MailTmCodeFetcher instance
    """
    fetcher = MailTmCodeFetcher(mail_tm_client, mail_tm_token)
    yield fetcher


@pytest.fixture
async def api_client(api_base_url):
    """Create HTTP client for Arknights API.

    Args:
        api_base_url: API base URL fixture

    Yields:
        httpx.AsyncClient configured for API calls
    """
    async with httpx.AsyncClient(base_url=api_base_url, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
async def game_credentials(api_base_url, mail_tm_client, mail_tm_token, test_email, test_server):
    """Authenticate once and cache credentials to avoid rate limiting.

    This fixture checks for cached credentials first. If valid cached credentials
    exist, they are reused. Otherwise, it performs the full authentication flow
    and caches the result for subsequent tests.

    Args:
        api_base_url: API base URL fixture
        mail_tm_client: MailTmClient fixture
        mail_tm_token: JWT token fixture
        test_email: Test email fixture
        test_server: Test server fixture

    Returns:
        Dict with 'channel_uid' and 'yostar_token' keys

    Raises:
        Exception: If authentication fails
    """
    # Try to load cached credentials first
    cached = load_credentials(test_email, test_server)
    if cached:
        logger.info(f"Using cached credentials for {test_email}")
        return cached

    logger.info(f"No valid cache found. Starting authentication flow for {test_email} on {test_server}")

    async with httpx.AsyncClient(base_url=api_base_url, timeout=30.0) as client:
        # Request authentication code
        logger.info("Requesting verification code from /auth/game-code")
        response = await client.post(
            "/auth/game-code",
            json={"email": test_email, "server": test_server}
        )
        response.raise_for_status()
        logger.info(f"Code request successful: {response.json()}")

        # Wait for verification code in email
        logger.info("Waiting for verification code in email (timeout: 90s)")
        fetcher = MailTmCodeFetcher(mail_tm_client, mail_tm_token)
        code = await fetcher.wait_for_code(timeout=90)
        logger.info(f"Code received: {code}")

        # Exchange code for game token
        logger.info("Exchanging code for game token via /auth/game-token")
        response = await client.post(
            "/auth/game-token",
            json={
                "email": test_email,
                "code": code,
                "server": test_server
            }
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Token exchange successful. Channel UID: {data['channel_uid'][:20]}...")

        credentials = {
            "channel_uid": data["channel_uid"],
            "yostar_token": data["yostar_token"]
        }

        # Cache credentials for future tests
        save_credentials(credentials, test_email, test_server)
        logger.info("Credentials cached for future tests")

        return credentials
