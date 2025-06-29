# AI Engine Service Tests

This directory contains comprehensive unit and integration tests for the AI Engine Service.

## Test Structure

- **`tests/ai_engine/test_analyze.py`** - Unit tests for the AIEngine analyze functionality
- **`tests/test_models_endpoint.py`** - Unit tests for the `/ai-engine/models` endpoint
- **`tests/test_analyze_endpoint.py`** - Unit tests for the `/ai-engine/analyze` endpoint
- **`tests/test_integration.py`** - Integration tests for the entire service
- **`tests/conftest.py`** - Pytest configuration and shared fixtures

## Key Features

### Mocking Strategy
All tests mock the `_hf_request` function to avoid making actual network calls to the HuggingFace API. This ensures:
- Fast test execution
- Reliable test results
- No dependency on external services
- No API rate limiting issues

### Test Coverage
The tests cover:
- ✅ Correct routing to endpoints
- ✅ Response schema conformity
- ✅ Error handling scenarios
- ✅ All analysis types (code_review, requirement_extraction, tech_recommendation, risk_assessment)
- ✅ Model validation and default selection
- ✅ Parameter passing
- ✅ Performance monitoring
- ✅ Concurrent request handling
- ✅ Unicode content support
- ✅ Large content handling

### Integration Testing
The integration tests spin up the service with TestClient and test:
- Complete workflows (get models → analyze content)
- Cross-endpoint functionality
- Error propagation
- Performance characteristics

## Running the Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Ensure you're in the service directory
cd /path/to/services/ai_engine_service
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suites
```bash
# Unit tests only
pytest tests/ai_engine/test_analyze.py tests/test_models_endpoint.py tests/test_analyze_endpoint.py -v

# Integration tests only  
pytest tests/test_integration.py -v

# Tests with specific markers
pytest -m "unit" -v
pytest -m "integration" -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Test Output Example
```
tests/ai_engine/test_analyze.py::TestAIEngineAnalyze::test_analyze_content_code_review_success PASSED
tests/ai_engine/test_analyze.py::TestAIEngineAnalyze::test_analyze_content_requirement_extraction_success PASSED
tests/test_models_endpoint.py::TestModelsEndpoint::test_get_models_success PASSED
tests/test_analyze_endpoint.py::TestAnalyzeEndpoint::test_analyze_content_success PASSED
tests/test_integration.py::TestAIEngineServiceIntegration::test_full_service_workflow PASSED
```

## Test Environment

The tests automatically set up a test environment with:
- Mocked HuggingFace API token
- Debug logging level
- Cache clearing between tests
- Clean module imports

## Mock Data

Tests use realistic mock data that matches the expected API responses:
- Generated text responses for analysis
- Classification labels and scores
- Model metadata
- Error responses

## Debugging Tests

To debug failing tests:

```bash
# Run with verbose output and no capture
pytest tests/test_name.py::test_function -v -s

# Run with pdb on failure
pytest tests/test_name.py::test_function --pdb

# Run with logging output
pytest tests/test_name.py::test_function -v --log-cli-level=DEBUG
```

## Adding New Tests

When adding new tests:

1. Use the existing fixtures in `conftest.py`
2. Mock `_hf_request` for any HuggingFace API calls
3. Test both success and error scenarios
4. Verify response schema conformity
5. Add appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

## Performance Considerations

The tests are designed to run quickly:
- All external API calls are mocked
- LRU caches are cleared between tests
- Minimal test data is used
- Tests can run in parallel with pytest-xdist
