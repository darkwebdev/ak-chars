"""Integration tests for Yostar's *public* (anonymous) player-search API.

Unlike test_roster_live.py, these need no test-account login at all, so
they carry none of that suite's rate-limit/credential-cache fragility -
they can run on every CI trigger. Purpose: catch it early if Yostar
changes the shape of its public search/expand response, independent of
whatever is happening with our own test account's credentials.

Assertions here are deliberately structural (field presence/type), not
value-based - a specific nickname search may legitimately return zero or
different results over time; what must stay stable is the *shape* of a
successful response.
"""
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_players_contract(api_client, test_server):
    """POST /players/search: anonymous nickname search, no credentials."""
    response = await api_client.post(
        "/players/search",
        json={"nickname": "a", "server": test_server, "limit": 5},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data.get("ok") is True
    assert "players" in data
    assert isinstance(data["players"], list)

    for player in data["players"]:
        assert "id" in player
        assert "name" in player


@pytest.mark.integration
@pytest.mark.asyncio
async def test_expand_players_contract(api_client, test_server):
    """POST /players/expand: anonymous id->summary lookup, no credentials.

    Uses a syntactically-plausible but almost certainly nonexistent id so
    the test doesn't depend on any specific real account continuing to
    exist - the goal is confirming the endpoint still accepts the request
    shape and responds with the expected envelope, not that this exact id
    resolves to a player.
    """
    response = await api_client.post(
        "/players/expand",
        json={"ids": ["999999999"], "server": test_server},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data.get("ok") is True
    assert "players" in data
    assert isinstance(data["players"], list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_graphql_search_players_contract(api_client, test_server):
    """Same contract as test_search_players_contract, via GraphQL."""
    query = """
    query SearchPlayers($nickname: String!, $server: String!) {
      searchPlayers(nickname: $nickname, server: $server, limit: 5) {
        ok
        players {
          playerId
          nickName
          level
        }
      }
    }
    """
    response = await api_client.post(
        "/graphql",
        json={"query": query, "variables": {"nickname": "a", "server": test_server}},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "errors" not in data, data.get("errors")
    result = data["data"]["searchPlayers"]
    assert result["ok"] is True
    assert isinstance(result["players"], list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_credentials_rejected_without_login(api_client, test_server):
    """/my/roster with garbage credentials should fail cleanly (not 200),
    independent of our own test account - confirms the auth-rejection
    path itself hasn't silently broken."""
    response = await api_client.post(
        "/my/roster",
        json={
            "channel_uid": "definitely-not-a-real-uid",
            "yostar_token": "definitely-not-a-real-token",
            "server": test_server,
        },
    )
    assert response.status_code != 200
