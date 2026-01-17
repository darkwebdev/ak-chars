# Server Tests

This directory contains tests for the FastAPI server endpoints and utilities.

## Test Files

- `test_api.py` - REST API endpoint tests using FastAPI TestClient
- `test_graphql.py` - GraphQL API endpoint tests (13 tests)
- `test_sanitization.py` - Tests for log sanitization functions
- `test_fixture.py` - Tests for fixture data structure and integrity
- `test_simple.py` - Simple standalone tests without pytest
- `user_data_response.json` - Fixture data for testing

## Running Tests

### Run all tests with pytest:

```bash
# From repository root
.venv/bin/python -m pytest server/tests/ -v

# Run specific test file
.venv/bin/python -m pytest server/tests/test_api.py -v

# Run specific test class
.venv/bin/python -m pytest server/tests/test_api.py::TestRosterEndpoint -v

# Run with coverage
.venv/bin/python -m pytest server/tests/ --cov=server --cov-report=html
```

### Run simple tests without pytest:

```bash
.venv/bin/python server/tests/test_simple.py
```

## Test Coverage

Tests cover:

- ✅ REST API endpoints (`/my/roster`, `/my/status`, `/auth/*`)
- ✅ GraphQL API (queries, filters, field selection)
- ✅ Request/response validation
- ✅ Fixture data integration
- ✅ Log sanitization (sensitive data redaction)
- ✅ Data structure validation
- ✅ Error handling

**Total: 51 tests**

## Fixture Data

The `user_data_response.json` file contains real game data structure but with redacted sensitive information. It's used for:

- Development mode testing (when `USE_FIXTURES=true`)
- Unit test validation
- API response structure verification

## Adding New Tests

When adding new tests:

1. Follow the existing test structure with classes
2. Use descriptive test names: `test_<what>_<condition>_<expected>`
3. Add docstrings explaining what the test validates
4. Group related tests in test classes
5. Use fixtures for shared test data

Example:

```python
class TestNewFeature:
    """Tests for new feature."""

    def test_feature_returns_correct_data(self):
        """Test that new feature returns expected data structure."""
        # Test implementation
        pass
```
