"""Tests for /my/roster endpoint using fixture data."""
import json
from pathlib import Path


def test_user_data_fixture_structure():
    """Verify the saved fixture has the expected structure."""
    fixture_path = Path(__file__).parent / "fixtures" / "user_data_response.json"
    
    with open(fixture_path) as f:
        response = json.load(f)
    
    # Check top-level structure
    assert response["ok"] is True
    assert "data" in response
    
    data = response["data"]
    assert "user" in data
    assert "result" in data
    
    # Check user structure
    user = data["user"]
    assert "troop" in user
    assert "inventory" in user
    assert "building" in user
    
    # Check roster
    roster = user["troop"]["chars"]
    assert isinstance(roster, dict)
    assert len(roster) > 0
    
    # Check a sample operator
    first_char = next(iter(roster.values()))
    assert "charId" in first_char
    assert "level" in first_char
    assert "evolvePhase" in first_char
    assert "potentialRank" in first_char
    assert "mainSkillLvl" in first_char
    assert "favorPoint" in first_char
    
    print(f"✓ Fixture contains {len(roster)} operators")
    print(f"✓ Sample operator: {first_char['charId']}")


if __name__ == "__main__":
    test_user_data_fixture_structure()
    print("All tests passed!")
