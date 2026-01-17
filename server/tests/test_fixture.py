"""Tests for fixture data structure and integrity."""
import json
from pathlib import Path
import pytest


def load_fixture():
    """Load fixture data."""
    fixture_path = Path(__file__).parent / 'user_data_response.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


class TestFixtureStructure:
    """Tests for fixture data structure."""
    
    def test_fixture_exists(self):
        """Test that fixture file exists."""
        fixture_path = Path(__file__).parent / 'user_data_response.json'
        assert fixture_path.exists(), "Fixture file should exist"
    
    def test_fixture_is_valid_json(self):
        """Test that fixture is valid JSON."""
        fixture_data = load_fixture()
        assert isinstance(fixture_data, dict)
    
    def test_fixture_top_level_structure(self):
        """Test fixture has expected top-level structure."""
        fixture_data = load_fixture()
        
        assert fixture_data["ok"] is True
        assert "data" in fixture_data
        assert isinstance(fixture_data["data"], dict)
    
    def test_fixture_has_user_data(self):
        """Test fixture contains user data."""
        fixture_data = load_fixture()
        
        data = fixture_data["data"]
        assert "user" in data
        assert "result" in data
    
    def test_fixture_has_roster(self):
        """Test fixture contains operator roster."""
        fixture_data = load_fixture()
        
        user = fixture_data["data"]["user"]
        assert "troop" in user
        
        troop = user["troop"]
        assert "chars" in troop
        assert isinstance(troop["chars"], dict)
        assert len(troop["chars"]) > 0
    
    def test_fixture_roster_operators(self):
        """Test fixture operators have expected fields."""
        fixture_data = load_fixture()
        
        chars = fixture_data["data"]["user"]["troop"]["chars"]
        
        # Check first operator
        first_char = next(iter(chars.values()))
        required_fields = [
            "charId", "level", "evolvePhase", "potentialRank",
            "mainSkillLvl", "favorPoint"
        ]
        
        for field in required_fields:
            assert field in first_char, f"Operator should have {field}"
    
    def test_fixture_has_status(self):
        """Test fixture contains user status."""
        fixture_data = load_fixture()
        
        user = fixture_data["data"]["user"]
        assert "status" in user
        
        status = user["status"]
        assert isinstance(status, dict)
    
    def test_fixture_status_fields(self):
        """Test fixture status has expected fields."""
        fixture_data = load_fixture()
        
        status = fixture_data["data"]["user"]["status"]
        required_fields = [
            "nickName", "level", "exp", "uid",
            "socialPoint", "recruitLicense"
        ]
        
        for field in required_fields:
            assert field in status, f"Status should have {field}"
    
    def test_fixture_operator_count(self):
        """Test fixture has reasonable number of operators."""
        fixture_data = load_fixture()
        
        chars = fixture_data["data"]["user"]["troop"]["chars"]
        char_count = len(chars)
        
        assert char_count > 0, "Should have at least 1 operator"
        assert char_count < 1000, "Should have reasonable number of operators"
        
        print(f"Fixture contains {char_count} operators")
    
    def test_fixture_has_amiya(self):
        """Test fixture contains Amiya (always given to players)."""
        fixture_data = load_fixture()
        
        chars = fixture_data["data"]["user"]["troop"]["chars"]
        
        # Find Amiya
        amiya = None
        for char in chars.values():
            if char.get("charId") == "char_002_amiya":
                amiya = char
                break
        
        assert amiya is not None, "Fixture should contain Amiya"
        assert amiya["level"] > 0, "Amiya should have positive level"


class TestFixtureDataTypes:
    """Tests for fixture data types."""
    
    def test_status_data_types(self):
        """Test status fields have correct data types."""
        fixture_data = load_fixture()
        status = fixture_data["data"]["user"]["status"]
        
        assert isinstance(status["nickName"], str)
        assert isinstance(status["level"], int)
        assert isinstance(status["exp"], int)
        assert isinstance(status["uid"], str)
    
    def test_operator_data_types(self):
        """Test operator fields have correct data types."""
        fixture_data = load_fixture()
        chars = fixture_data["data"]["user"]["troop"]["chars"]
        
        first_char = next(iter(chars.values()))
        
        assert isinstance(first_char["charId"], str)
        assert isinstance(first_char["level"], int)
        assert isinstance(first_char["evolvePhase"], int)
        assert isinstance(first_char["potentialRank"], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
