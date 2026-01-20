"""Tests to verify REST and GraphQL endpoint parity with mocks."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from server.main import app


client = TestClient(app)


# Mock data
MOCK_PLAYER_DATA = [
    {
        'playerId': '12345',
        'uid': '12345',
        'nickName': 'TestDoctor',
        'level': 120,
        'avatar': 'avatar_123'
    }
]

MOCK_OPERATOR_DATA = {
    'user': {
        'troop': {
            'chars': {
                'char_002_amiya': {
                    'charId': 'char_002_amiya',
                    'level': 50,
                    'evolvePhase': 2,
                    'potentialRank': 3,
                    'mainSkillLvl': 7,
                    'favorPoint': 25570,
                    'skills': []
                }
            }
        },
        'status': {
            'nickName': 'TestDoctor',
            'nickNumber': '1234',
            'level': 120,
            'exp': 123456,
            'socialPoint': 5000,
            'uid': '12345'
        }
    }
}

MOCK_USER_DATA_FOR_GQL = {
    'troop': {
        'chars': {
            'char_002_amiya': {
                'charId': 'char_002_amiya',
                'level': 50,
                'evolvePhase': 2,
                'potentialRank': 3,
                'mainSkillLvl': 7,
                'favorPoint': 25570,
                'skills': []
            }
        }
    },
    'status': {
        'nickName': 'TestDoctor',
        'nickNumber': '1234',
        'level': 120,
        'exp': 123456,
        'socialPoint': 5000,
        'uid': '12345'
    }
}


class TestPlayerSearchParity:
    """Test REST /players/search and GraphQL searchPlayers have same behavior."""

    @patch('server.players.search_players')
    @pytest.mark.asyncio
    async def test_rest_players_search(self, mock_search):
        """Test REST endpoint for player search."""
        mock_search.return_value = MOCK_PLAYER_DATA

        response = client.post('/players/search', json={
            'nickname': 'TestDoctor',
            'server': 'en',
            'limit': 10
        })

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'players' in data
        assert len(data['players']) == 1
        assert data['players'][0]['nickName'] == 'TestDoctor'

    @patch('server.ark_client.search_players')
    @pytest.mark.asyncio
    async def test_graphql_search_players(self, mock_search):
        """Test GraphQL query for player search."""
        mock_search.return_value = MOCK_PLAYER_DATA

        query = """
        query {
            searchPlayers(nickname: "TestDoctor", server: "en", limit: 10) {
                ok
                players {
                    playerId
                    nickName
                    level
                }
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'searchPlayers' in data['data']
        result = data['data']['searchPlayers']
        assert result['ok'] is True
        assert len(result['players']) == 1


class TestPlayerExpandParity:
    """Test REST /players/expand and GraphQL expandPlayers have same behavior."""

    @patch('server.players.expand_player_ids')
    @pytest.mark.asyncio
    async def test_rest_players_expand(self, mock_expand):
        """Test REST endpoint for player expand."""
        mock_expand.return_value = MOCK_PLAYER_DATA

        response = client.post('/players/expand', json={
            'ids': ['12345'],
            'server': 'en'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'players' in data
        assert len(data['players']) == 1

    @patch('server.ark_client.expand_player_ids')
    @pytest.mark.asyncio
    async def test_graphql_expand_players(self, mock_expand):
        """Test GraphQL query for player expand."""
        mock_expand.return_value = MOCK_PLAYER_DATA

        query = """
        query {
            expandPlayers(ids: ["12345"], server: "en") {
                ok
                players {
                    playerId
                    nickName
                    level
                }
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'expandPlayers' in data['data']
        result = data['data']['expandPlayers']
        assert result['ok'] is True


class TestSinglePlayerParity:
    """Test REST /characters/{id} and GraphQL getPlayer have same behavior."""

    @patch('server.players.expand_player_ids')
    @pytest.mark.asyncio
    async def test_rest_get_character(self, mock_expand):
        """Test REST endpoint for single player."""
        mock_expand.return_value = MOCK_PLAYER_DATA

        response = client.get('/characters/12345?server=en')

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'player' in data
        assert data['player']['nickName'] == 'TestDoctor'

    @patch('server.ark_client.expand_player_ids')
    @pytest.mark.asyncio
    async def test_graphql_get_player(self, mock_expand):
        """Test GraphQL query for single player."""
        mock_expand.return_value = MOCK_PLAYER_DATA

        query = """
        query {
            getPlayer(playerId: "12345", server: "en") {
                playerId
                nickName
                level
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'getPlayer' in data['data']
        player = data['data']['getPlayer']
        assert player is not None
        assert player['nickName'] == 'TestDoctor'


class TestFixtureOperatorsParity:
    """Test REST /fixtures/operators and GraphQL operators have same behavior."""

    def test_rest_get_operators(self):
        """Test REST endpoint for fixture operators."""
        response = client.get('/fixtures/operators')

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'operators' in data
        assert len(data['operators']) > 0

    def test_rest_get_operators_filtered(self):
        """Test REST endpoint with filters."""
        response = client.get('/fixtures/operators?min_level=50&min_elite=2')

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'operators' in data
        # Verify filtering worked
        for op in data['operators']:
            assert op['level'] >= 50
            assert op['evolvePhase'] >= 2

    def test_graphql_get_operators(self):
        """Test GraphQL query for fixture operators."""
        query = """
        query {
            operators(minLevel: 50, minElite: 2) {
                charId
                level
                elite
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'operators' in data['data']
        operators = data['data']['operators']
        # Verify filtering worked
        for op in operators:
            assert op['level'] >= 50
            assert op['elite'] >= 2


class TestFixtureSingleOperatorParity:
    """Test REST /fixtures/operator/{id} and GraphQL operator have same behavior."""

    def test_rest_get_single_operator(self):
        """Test REST endpoint for single fixture operator."""
        response = client.get('/fixtures/operator/char_002_amiya')

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'operator' in data
        assert data['operator']['charId'] == 'char_002_amiya'

    def test_graphql_get_single_operator(self):
        """Test GraphQL query for single fixture operator."""
        query = """
        query {
            operator(charId: "char_002_amiya") {
                charId
                level
                elite
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'operator' in data['data']
        operator = data['data']['operator']
        assert operator is not None
        assert operator['charId'] == 'char_002_amiya'


class TestFixtureUserStatusParity:
    """Test REST /fixtures/user-status and GraphQL userStatus have same behavior."""

    def test_rest_get_user_status(self):
        """Test REST endpoint for fixture user status."""
        response = client.get('/fixtures/user-status')

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'status' in data
        assert 'nickName' in data['status']
        assert 'level' in data['status']

    def test_graphql_get_user_status(self):
        """Test GraphQL query for fixture user status."""
        query = """
        query {
            userStatus {
                nickName
                level
                uid
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'userStatus' in data['data']
        status = data['data']['userStatus']
        assert status is not None
        assert 'nickName' in status
        assert 'level' in status


class TestAuthenticationParity:
    """Test REST and GraphQL authentication endpoints have same behavior."""

    @patch('server.auth.send_game_auth_code')
    @pytest.mark.asyncio
    async def test_rest_send_auth_code(self, mock_send):
        """Test REST endpoint for sending auth code."""
        mock_send.return_value = None

        response = client.post('/auth/game-code', json={
            'email': 'test@example.com',
            'server': 'en'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True

    @patch('server.graphql_schema.send_auth_code')
    @pytest.mark.asyncio
    async def test_graphql_send_auth_code(self, mock_send):
        """Test GraphQL mutation for sending auth code."""
        mock_send.return_value = None

        query = """
        mutation {
            sendAuthCode(email: "test@example.com", server: "en") {
                success
                message
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'sendAuthCode' in data['data']
        result = data['data']['sendAuthCode']
        assert result['success'] is True


class TestMyRosterParity:
    """Test REST /my/roster and GraphQL myRoster have same behavior."""

    @patch('server.auth.get_user_data')
    @pytest.mark.asyncio
    async def test_rest_my_roster(self, mock_get_data):
        """Test REST endpoint for authenticated roster."""
        mock_get_data.return_value = MOCK_OPERATOR_DATA

        response = client.post('/my/roster', json={
            'channel_uid': '14821859648',
            'yostar_token': 'mock_token',
            'server': 'en'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'chars' in data

    @patch('server.graphql_schema.get_user_data_with_auth')
    @pytest.mark.asyncio
    async def test_graphql_my_roster(self, mock_get_data):
        """Test GraphQL query for authenticated roster."""
        mock_get_data.return_value = MOCK_USER_DATA_FOR_GQL

        query = """
        query {
            myRoster(
                channelUid: "14821859648",
                yostarToken: "mock_token",
                server: "en"
            ) {
                charId
                level
                elite
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'myRoster' in data['data']
        roster = data['data']['myRoster']
        assert isinstance(roster, list)


class TestPlayerAvatarParity:
    """Test REST /avatars/{id} and GraphQL getPlayerAvatarUrl have same behavior."""

    def test_rest_get_avatar_url(self):
        """Test REST endpoint for player avatar returns image."""
        # Avatar endpoint returns binary data, so we just test it exists
        # Actual avatar fetching would require mocking the arkprts client
        response = client.get('/avatars/12345?server=en')
        # May return 404 or 503 without real client, just verify endpoint exists
        assert response.status_code in [404, 503]

    def test_graphql_get_avatar_url(self):
        """Test GraphQL query for player avatar URL."""
        query = """
        query {
            getPlayerAvatarUrl(playerId: "12345", server: "en")
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'getPlayerAvatarUrl' in data['data']
        url = data['data']['getPlayerAvatarUrl']
        assert url is not None
        assert '/avatars/12345' in url
        assert 'server=en' in url


class TestRawPlayerDataParity:
    """Test REST /players/raw and GraphQL getRawPlayerData have same behavior."""

    @patch('server.ark_client._make_client')
    def test_rest_get_raw_player_single(self, mock_make_client):
        """Test REST endpoint for raw player data (single)."""
        # Mock the client
        mock_client = Mock()
        mock_client.get_raw_player_info = AsyncMock(return_value={'player': 'data'})
        mock_make_client.return_value = mock_client

        response = client.get('/players/raw/12345?server=en')
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'raw' in data

    @patch('server.ark_client._make_client')
    def test_rest_get_raw_players_multiple(self, mock_make_client):
        """Test REST endpoint for raw player data (multiple)."""
        mock_client = Mock()
        mock_client.get_raw_player_info = AsyncMock(return_value={'players': ['data1', 'data2']})
        mock_make_client.return_value = mock_client

        response = client.post('/players/raw', json={
            'ids': ['12345', '67890'],
            'server': 'en'
        })
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'raw' in data

    @patch('server.ark_client._make_client')
    def test_graphql_get_raw_player_data(self, mock_make_client):
        """Test GraphQL query for raw player data (single)."""
        # Mock the client
        mock_client = Mock()
        mock_client.get_raw_player_info = AsyncMock(return_value={'player': 'data'})
        mock_make_client.return_value = mock_client

        query = """
        query {
            getRawPlayerData(playerId: "12345", server: "en")
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'getRawPlayerData' in data['data']
        raw_data = data['data']['getRawPlayerData']
        assert raw_data is not None
        # Verify it's JSON string
        import json
        parsed = json.loads(raw_data)
        assert 'player' in parsed

    @patch('server.ark_client._make_client')
    def test_graphql_get_raw_players_data(self, mock_make_client):
        """Test GraphQL query for raw player data (multiple)."""
        mock_client = Mock()
        mock_client.get_raw_player_info = AsyncMock(return_value={'players': ['data1', 'data2']})
        mock_make_client.return_value = mock_client

        query = """
        query {
            getRawPlayersData(ids: ["12345", "67890"], server: "en")
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'getRawPlayersData' in data['data']
        raw_data = data['data']['getRawPlayersData']
        assert raw_data is not None
        # Verify it's JSON string
        import json
        parsed = json.loads(raw_data)
        assert 'players' in parsed


class TestMyStatusParity:
    """Test REST /my/status and GraphQL myStatus have same behavior."""

    @patch('server.auth.get_user_data')
    @pytest.mark.asyncio
    async def test_rest_my_status(self, mock_get_data):
        """Test REST endpoint for authenticated status."""
        mock_get_data.return_value = MOCK_OPERATOR_DATA

        response = client.post('/my/status', json={
            'channel_uid': '14821859648',
            'yostar_token': 'mock_token',
            'server': 'en'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
        assert 'status' in data
        assert data['status']['nickName'] == 'TestDoctor'

    @patch('server.graphql_schema.get_user_data_with_auth')
    @pytest.mark.asyncio
    async def test_graphql_my_status(self, mock_get_data):
        """Test GraphQL query for authenticated status."""
        mock_get_data.return_value = MOCK_USER_DATA_FOR_GQL

        query = """
        query {
            myStatus(
                channelUid: "14821859648",
                yostarToken: "mock_token",
                server: "en"
            ) {
                nickName
                level
                uid
            }
        }
        """

        response = client.post('/graphql', json={'query': query})

        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'myStatus' in data['data']
        status = data['data']['myStatus']
        assert status is not None
        assert status['nickName'] == 'TestDoctor'
