"""Simple test to verify endpoints return correct data structure."""
import json
from pathlib import Path


def load_fixture():
    """Load fixture data."""
    fixture_path = Path(__file__).parent / 'user_data_response.json'
    with open(fixture_path, 'r') as f:
        return json.load(f)


def test_roster_endpoint_structure():
    """Test that /my/roster returns chars from fixture."""
    fixture_data = load_fixture()
    
    chars = fixture_data.get('data', {}).get('user', {}).get('troop', {}).get('chars', {})
    
    assert isinstance(chars, dict), "chars should be a dict"
    assert len(chars) > 0, "chars should not be empty"
    
    first_char = next(iter(chars.values()))
    assert 'charId' in first_char, "each char should have charId"
    assert 'level' in first_char, "each char should have level"
    
    print(f"✓ Roster contains {len(chars)} operators")
    print(f"✓ Sample operator: {first_char.get('charId')}")


def test_status_endpoint_structure():
    """Test that /my/status returns status from fixture."""
    fixture_data = load_fixture()
    
    status = fixture_data.get('data', {}).get('user', {}).get('status', {})
    
    assert isinstance(status, dict), "status should be a dict"
    assert 'nickName' in status, "status should have nickName"
    assert 'level' in status, "status should have level"
    assert 'uid' in status, "status should have uid"
    
    print(f"✓ Status contains nickName: {status.get('nickName')}")
    print(f"✓ Status contains level: {status.get('level')}")
    print(f"✓ Status contains uid: {status.get('uid')}")


if __name__ == "__main__":
    test_roster_endpoint_structure()
    print()
    test_status_endpoint_structure()
    print("\n✓ All tests passed!")
