"""Integration tests for roster and status APIs with live credentials."""

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_roster_with_real_credentials(api_client, game_credentials, test_server):
    """Test fetching roster with real authenticated credentials.

    Verifies that the /my/roster endpoint works with live credentials
    and returns properly structured operator data.
    """
    response = await api_client.post(
        "/my/roster",
        json={
            "channel_uid": game_credentials["channel_uid"],
            "yostar_token": game_credentials["yostar_token"],
            "server": test_server
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data.get("ok") is True
    assert "chars" in data

    # Verify operators data
    chars = data["chars"]
    assert isinstance(chars, dict)
    assert len(chars) > 0

    # Verify operator structure (check first operator)
    first_char = next(iter(chars.values()))
    assert "charId" in first_char
    assert "level" in first_char
    assert isinstance(first_char["level"], int)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_status_with_real_credentials(api_client, game_credentials, test_server):
    """Test fetching account status with real credentials.

    Verifies that the /my/status endpoint returns valid account information.
    """
    response = await api_client.post(
        "/my/status",
        json={
            "channel_uid": game_credentials["channel_uid"],
            "yostar_token": game_credentials["yostar_token"],
            "server": test_server
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data.get("ok") is True
    assert "status" in data

    # Verify status fields
    status = data["status"]
    assert "nickName" in status or "nickname" in status
    assert "level" in status
    assert "uid" in status

    # Verify data types
    level = status.get("level")
    if level is not None:
        assert isinstance(level, int)
        assert level > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_graphql_operators_query(api_client, game_credentials, test_server):
    """Test GraphQL operators query with real data.

    Verifies that the GraphQL endpoint works with live credentials
    and returns operator results.
    """
    query = """
    query GetOperators($channelUid: String!, $yostarToken: String!, $server: String!) {
      myRoster(channelUid: $channelUid, yostarToken: $yostarToken, server: $server) {
        charId
        level
        elite
      }
    }
    """

    response = await api_client.post(
        "/graphql",
        json={
            "query": query,
            "variables": {
                "channelUid": game_credentials["channel_uid"],
                "yostarToken": game_credentials["yostar_token"],
                "server": test_server
            }
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify GraphQL response structure
    assert "data" in data
    assert "myRoster" in data["data"]

    # Verify operators returned
    operators = data["data"]["myRoster"]
    assert isinstance(operators, list)
    assert len(operators) > 0

    # Verify operator structure
    first_op = operators[0]
    assert "charId" in first_op
    assert "level" in first_op
    assert isinstance(first_op["level"], int)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_credentials_rejected(api_client, test_server):
    """Test that fake credentials are rejected.

    Verifies that the server properly validates credentials and rejects
    invalid ones with appropriate error responses.
    """
    response = await api_client.post(
        "/my/roster",
        json={
            "channel_uid": "fake_channel_uid_12345",
            "yostar_token": "fake_yostar_token_67890",
            "server": test_server
        }
    )

    # Should return error status (not 200)
    assert response.status_code != 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_roster_filtering(api_client, game_credentials, test_server):
    """Test roster data can be filtered by level.

    Verifies that the roster data structure allows for client-side filtering.
    """
    # Get full roster via GraphQL
    query = """
    query GetOperators($channelUid: String!, $yostarToken: String!, $server: String!) {
      myRoster(channelUid: $channelUid, yostarToken: $yostarToken, server: $server) {
        charId
        level
      }
    }
    """

    response = await api_client.post(
        "/graphql",
        json={
            "query": query,
            "variables": {
                "channelUid": game_credentials["channel_uid"],
                "yostarToken": game_credentials["yostar_token"],
                "server": test_server
            }
        }
    )

    assert response.status_code == 200
    data = response.json()
    operators = data["data"]["myRoster"]

    # Test client-side filtering
    if operators:
        # Find max level
        max_level = max(op["level"] for op in operators)

        # Filter operators with max level
        high_level_ops = [op for op in operators if op["level"] >= max_level]

        # Verify filtering worked correctly
        assert len(high_level_ops) > 0
        for op in high_level_ops:
            assert op["level"] >= max_level
