"""Tests for GraphQL API endpoints."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


class TestGraphQLOperators:
    """Tests for GraphQL operators queries."""
    
    def test_graphql_endpoint_exists(self):
        """Test that GraphQL endpoint is accessible."""
        response = client.post(
            "/graphql",
            json={"query": "{ __typename }"}
        )
        assert response.status_code == 200
    
    def test_query_all_operators(self):
        """Test querying all operators with selected fields."""
        query = """
        {
          operators {
            charId
            level
            elite
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "operators" in data["data"]
        assert len(data["data"]["operators"]) > 0
        
        # Check structure
        first_op = data["data"]["operators"][0]
        assert "charId" in first_op
        assert "level" in first_op
        assert "elite" in first_op
    
    def test_query_operators_with_filters(self):
        """Test querying operators with level filter."""
        query = """
        {
          operators(minLevel: 80) {
            charId
            level
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        operators = data["data"]["operators"]
        assert all(op["level"] >= 80 for op in operators)
    
    def test_query_operators_with_elite_filter(self):
        """Test querying operators with elite filter."""
        query = """
        {
          operators(minElite: 2) {
            charId
            elite
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        operators = data["data"]["operators"]
        assert all(op["elite"] >= 2 for op in operators)
    
    def test_query_operators_with_multiple_filters(self):
        """Test querying operators with multiple filters."""
        query = """
        {
          operators(minLevel: 70, maxLevel: 80, minElite: 2) {
            charId
            level
            elite
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        operators = data["data"]["operators"]
        for op in operators:
            assert 70 <= op["level"] <= 80
            assert op["elite"] >= 2
    
    def test_query_operators_with_ids_filter(self):
        """Test querying specific operators by IDs."""
        query = """
        {
          operators(ids: ["char_002_amiya", "char_151_myrtle"]) {
            charId
            level
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        operators = data["data"]["operators"]
        char_ids = [op["charId"] for op in operators]
        
        assert "char_002_amiya" in char_ids or "char_151_myrtle" in char_ids
    
    def test_query_single_operator(self):
        """Test querying a single operator by ID."""
        query = """
        {
          operator(charId: "char_002_amiya") {
            charId
            level
            elite
            potential
            trust
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        operator = data["data"]["operator"]
        assert operator is not None
        assert operator["charId"] == "char_002_amiya"
        assert "level" in operator
        assert "elite" in operator
        assert "potential" in operator
        assert "trust" in operator
    
    def test_query_operator_not_found(self):
        """Test querying non-existent operator."""
        query = """
        {
          operator(charId: "char_999_notexist") {
            charId
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        assert data["data"]["operator"] is None
    
    def test_query_operators_custom_fields(self):
        """Test querying operators with custom field selection."""
        query = """
        {
          operators(minLevel: 50) {
            charId
            skillLevel
            potential
            trust
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        operators = data["data"]["operators"]
        assert len(operators) > 0
        
        first_op = operators[0]
        assert "charId" in first_op
        assert "skillLevel" in first_op
        assert "potential" in first_op
        assert "trust" in first_op
        # These fields should NOT be in the response
        assert "level" not in first_op or first_op.get("level") is None


class TestGraphQLUserStatus:
    """Tests for GraphQL user status queries."""
    
    def test_query_user_status(self):
        """Test querying user status."""
        query = """
        {
          userStatus {
            nickName
            level
            uid
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        status = data["data"]["userStatus"]
        assert status is not None
        assert "nickName" in status
        assert "level" in status
        assert "uid" in status
    
    def test_query_user_status_display_name(self):
        """Test querying user status with computed field."""
        query = """
        {
          userStatus {
            displayName
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        status = data["data"]["userStatus"]
        assert "displayName" in status
        assert "#" in status["displayName"]


class TestGraphQLErrors:
    """Tests for GraphQL error handling."""
    
    def test_invalid_query(self):
        """Test that invalid queries return errors."""
        query = """
        {
          invalidField {
            charId
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        assert "errors" in data
    
    def test_missing_required_argument(self):
        """Test that missing required arguments return errors."""
        query = """
        {
          operator {
            charId
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        data = response.json()
        
        assert "errors" in data


class TestGraphQLAuthentication:
    """Tests for GraphQL authentication mutations and queries."""
    
    def test_send_auth_code(self):
        """Test sending authentication code via GraphQL."""
        query = """
        mutation {
          sendAuthCode(email: "test@example.com") {
            success
            message
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "sendAuthCode" in data["data"]
        result = data["data"]["sendAuthCode"]
        assert "success" in result
        assert "message" in result
    
    def test_get_auth_token_failure(self):
        """Test getting auth token with invalid code."""
        query = """
        mutation {
          getAuthToken(email: "test@example.com", code: "000000") {
            success
            channelUid
            yostarToken
            error
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "getAuthToken" in data["data"]
        result = data["data"]["getAuthToken"]
        assert result["success"] is False
        assert result["channelUid"] is None
        assert result["yostarToken"] is None
        assert result["error"] is not None
    
    def test_my_roster(self):
        """Test querying user's roster via GraphQL."""
        query = """
        {
          myRoster(channelUid: "test", yostarToken: "test") {
            charId
            level
            elite
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "myRoster" in data["data"]
        roster = data["data"]["myRoster"]
        assert len(roster) > 0
        
        first_char = roster[0]
        assert "charId" in first_char
        assert "level" in first_char
        assert "elite" in first_char
    
    def test_my_status(self):
        """Test querying user's status via GraphQL."""
        query = """
        {
          myStatus(channelUid: "test", yostarToken: "test") {
            level
            exp
            uid
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "myStatus" in data["data"]
        status = data["data"]["myStatus"]
        assert "level" in status
        assert "exp" in status
        assert "uid" in status
        assert status["level"] > 0

    def test_my_inventory(self):
        """Test querying user's currency inventory via GraphQL."""
        query = """
        {
          myInventory(channelUid: "test", yostarToken: "test") {
            orundum
            originitePrime
            headhuntingPermits
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "myInventory" in data["data"]
        inventory = data["data"]["myInventory"]
        assert "orundum" in inventory
        assert "originitePrime" in inventory
        assert "headhuntingPermits" in inventory
        assert isinstance(inventory["orundum"], int)
        assert isinstance(inventory["originitePrime"], int)
        assert isinstance(inventory["headhuntingPermits"], int)

        # Real values from the fixture's status block (diamondShard=12890,
        # payDiamond=0, freeDiamond=545, gachaTicket=0). Pinned as exact
        # values, not just type checks - a prior version of this resolver
        # read from the generic per-item inventory map instead of these
        # dedicated status fields and silently always returned 0 for all
        # three, which type-only assertions didn't catch. headhuntingPermits
        # is 0 here deliberately, not a leftover placeholder: an earlier fix
        # wired this to status.recruitLicense (21 in this fixture), which
        # reads sensibly but is actually Recruitment Permit, a different
        # resource - status.gachaTicket is the real Headhunting Permit
        # field, and happens to be 0 for this account.
        assert inventory["orundum"] == 12890
        assert inventory["originitePrime"] == 545
        assert inventory["headhuntingPermits"] == 0

    @patch('server.graphql_schema.get_user_data_with_auth')
    @pytest.mark.asyncio
    async def test_my_inventory_reads_the_right_status_fields(self, mock_get_data):
        """Distinguish the correct status fields from similarly-named
        neighbors with a mock, rather than relying on the real fixture's
        values (which happen to be 0 for headhuntingPermits, so an earlier
        version of this test couldn't have caught headhuntingPermits being
        wired to the wrong field - it was, twice, in production)."""
        mock_get_data.return_value = {
            'status': {
                'diamondShard': 111,      # orundum
                'payDiamond': 22,
                'freeDiamond': 33,        # originitePrime = 22 + 33 = 55
                'gachaTicket': 444,       # headhuntingPermits - real Headhunting Permit
                'recruitLicense': 999,    # decoy: Recruitment Permit, a different resource
            },
            'inventory': {},
        }

        query = """
        {
          myInventory(channelUid: "test", yostarToken: "test") {
            orundum
            originitePrime
            headhuntingPermits
          }
        }
        """
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200

        inventory = response.json()["data"]["myInventory"]
        assert inventory["orundum"] == 111
        assert inventory["originitePrime"] == 55
        assert inventory["headhuntingPermits"] == 444


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
