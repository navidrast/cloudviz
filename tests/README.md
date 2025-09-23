# CloudViz Test Suite

This directory contains the test suite for CloudViz.

## Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for API endpoints and workflows
- `fixtures/` - Test data and mock objects

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=cloudviz --cov-report=html
```

## Test Guidelines

- Write tests for new functionality
- Test edge cases and error conditions
- Use descriptive test names
- Mock external services
- Keep tests isolated and independent