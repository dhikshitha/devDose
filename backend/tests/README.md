# Backend Tests

This directory contains all test files for the Tech Learning Companion backend.

## Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_auth_endpoints.py` - Tests for authentication endpoints

## Running Tests

### Unit Tests with Pytest
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth_endpoints.py

# Run with verbose output
pytest -v
```


## Test Coverage

### Phase 1: Authentication
- [x] Health check endpoint
- [x] User registration
- [x] User login
- [x] JWT token validation
- [x] Profile retrieval
- [x] Profile updates
- [x] Password change
- [x] Token refresh

### Future Phases
- [ ] Content delivery endpoints
- [ ] Challenge system endpoints
- [ ] Progress tracking endpoints
- [ ] Spaced repetition endpoints