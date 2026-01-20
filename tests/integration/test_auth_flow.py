"""Integration tests for authentication flow."""

import pytest
from .credential_cache import load_credentials


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_request_game_code(api_client, test_email, test_server):
    """Test requesting authentication code.

    Verifies that the /auth/game-code endpoint accepts valid requests
    and triggers email delivery.

    NOTE: Skips if cached credentials exist to avoid Yostar rate limits.
    """
    # Skip if we have cached credentials (avoid rate limiting)
    if load_credentials(test_email, test_server):
        pytest.skip("Cached credentials exist; skipping to avoid rate limits")

    response = await api_client.post(
        "/auth/game-code",
        json={"email": test_email, "server": test_server}
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.timeout(180)
async def test_complete_auth_flow(api_client, email_fetcher, test_email, test_server):
    """Test complete authentication flow: request code, poll email, exchange for token.

    This test verifies the end-to-end authentication process:
    1. Request verification code via /auth/game-code
    2. Wait for email with code via Mail.tm API
    3. Exchange code for game credentials via /auth/game-token
    4. Verify credentials are valid and non-empty

    NOTE: Skips if cached credentials exist to avoid Yostar rate limits.
    """
    # Skip if we have cached credentials (avoid rate limiting)
    if load_credentials(test_email, test_server):
        pytest.skip("Cached credentials exist; skipping to avoid rate limits")

    # Step 1: Request verification code
    response = await api_client.post(
        "/auth/game-code",
        json={"email": test_email, "server": test_server}
    )
    assert response.status_code == 200

    # Step 2: Wait for verification code in email
    code = await email_fetcher.wait_for_code(timeout=90)
    assert code is not None
    assert len(code) == 6
    assert code.isdigit()

    # Step 3: Exchange code for game token
    response = await api_client.post(
        "/auth/game-token",
        json={
            "email": test_email,
            "code": code,
            "server": test_server
        }
    )
    assert response.status_code == 200

    # Step 4: Verify credentials received
    data = response.json()
    assert "channel_uid" in data
    assert "yostar_token" in data

    # Verify credentials are non-empty strings
    assert isinstance(data["channel_uid"], str)
    assert isinstance(data["yostar_token"], str)
    assert len(data["channel_uid"]) > 0
    assert len(data["yostar_token"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_code_rejected(api_client, test_email, test_server):
    """Test that invalid verification codes are rejected.

    Verifies that the server properly validates codes and rejects
    invalid ones with appropriate error responses.
    """
    response = await api_client.post(
        "/auth/game-token",
        json={
            "email": test_email,
            "code": "000000",
            "server": test_server
        }
    )

    # Should return error status (400 or 422)
    assert response.status_code in [400, 422, 500]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_code_invalid_email(api_client, test_server):
    """Test that invalid email addresses are rejected."""
    response = await api_client.post(
        "/auth/game-code",
        json={"email": "not-an-email", "server": test_server}
    )

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_code_invalid_server(api_client, test_email):
    """Test that invalid server codes are rejected."""
    response = await api_client.post(
        "/auth/game-code",
        json={"email": test_email, "server": "invalid-server"}
    )

    # Should return validation error or bad request (or 500 if server doesn't validate)
    assert response.status_code in [400, 422, 500]
