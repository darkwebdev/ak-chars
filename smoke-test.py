#!/usr/bin/env python3
"""
Smoke tests for deployed ak-chars API server.
Verifies production deployment at https://ak-chars-api.fly.dev
"""

import httpx
import sys

BASE_URL = "https://ak-chars-api.fly.dev"
TIMEOUT = 30.0


def test_health():
    """Test server is responding."""
    print("✓ Testing server health...")
    try:
        response = httpx.get(f"{BASE_URL}/graphql", timeout=TIMEOUT)
        assert response.status_code in [200, 405], f"Unexpected status: {response.status_code}"
        print(f"  Server is up (status {response.status_code})")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_graphql_endpoint():
    """Test GraphQL endpoint with simple query."""
    print("✓ Testing GraphQL endpoint...")
    try:
        query = """
        query {
            operators(ids: ["char_002_amiya"]) {
                charId
                level
            }
        }
        """
        response = httpx.post(
            f"{BASE_URL}/graphql",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "data" in data, "Response missing 'data' field"
        assert "operators" in data["data"], "Response missing 'operators' field"

        operators = data["data"]["operators"]
        assert len(operators) > 0, "Expected at least one operator"
        assert operators[0]["charId"] == "char_002_amiya", "Wrong operator returned"

        print(f"  GraphQL working (returned {len(operators)} operator(s))")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_auth_code_endpoint():
    """Test auth code request endpoint (should reject invalid email)."""
    print("✓ Testing auth code endpoint...")
    try:
        response = httpx.post(
            f"{BASE_URL}/auth/game-code",
            json={"email": "invalid-email", "server": "en"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        # Should return 422 for invalid email format
        assert response.status_code == 422, f"Expected 422 for invalid email, got {response.status_code}"
        print(f"  Auth endpoint validates input correctly")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_roster_endpoint():
    """Test roster endpoint (should reject missing credentials)."""
    print("✓ Testing roster endpoint...")
    try:
        response = httpx.post(
            f"{BASE_URL}/my/roster",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        # Should return 422 for missing required fields
        assert response.status_code == 422, f"Expected 422 for missing fields, got {response.status_code}"
        print(f"  Roster endpoint validates input correctly")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def test_cors_headers():
    """Test CORS headers are set correctly."""
    print("✓ Testing CORS configuration...")
    try:
        response = httpx.options(
            f"{BASE_URL}/graphql",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            },
            timeout=TIMEOUT
        )

        # Check CORS headers are present
        assert "access-control-allow-origin" in response.headers, "Missing CORS allow-origin header"
        print(f"  CORS configured correctly")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


def main():
    """Run all smoke tests."""
    print(f"\n🔥 Smoke Testing: {BASE_URL}\n")

    tests = [
        test_health,
        test_graphql_endpoint,
        test_auth_code_endpoint,
        test_roster_endpoint,
        test_cors_headers,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            sys.exit(1)
        print()

    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 50)

    if passed == total:
        print("✅ All smoke tests passed!")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
