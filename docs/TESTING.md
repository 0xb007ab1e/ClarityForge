# Testing & CI Pipeline

This document outlines the comprehensive testing strategy and CI/CD pipeline for ClarityForge.

## Testing Strategy

### Test Types

1. **Unit Tests** - Test individual components in isolation
   - Located in `tests/test_plan_engine.py`
   - Focus on business logic and core functionality
   - Use mocking for external dependencies

2. **API Tests** - Test FastAPI endpoints
   - Located in `tests/test_api.py`
   - Use `httpx.AsyncClient` for async testing
   - Cover both sync and async endpoint behavior
   - Test error conditions and edge cases

3. **Integration Tests** - Test component interactions
   - Run with marker `integration`
   - Test full workflows and data flow

### Test Configuration

Tests are configured via `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "api: marks tests as API tests",
    "slow: marks tests as slow running",
]
asyncio_mode = "auto"
```

### Coverage Requirements

- **Minimum Coverage**: 80%
- **Coverage Configuration**: Defined in `pyproject.toml`
- **Excluded Files**: Test files, `__main__.py`, and other non-essential files
- **Reports**: Generated in HTML and XML formats

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   poetry install --with dev
   ```

2. Set up pre-commit hooks (optional but recommended):
   ```bash
   make dev-setup
   ```

### Test Commands

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run API tests only
make test-api

# Run integration tests only
make test-integration

# Run all tests with coverage
make test-all

# Generate coverage report
make coverage
```

### Manual Commands

```bash
# Run specific test files
poetry run pytest tests/test_plan_engine.py -v

# Run tests with specific markers
poetry run pytest -m "unit" -v

# Run tests with coverage
poetry run coverage run -m pytest tests/
poetry run coverage report --show-missing
```

## Code Quality

### Linting & Formatting

The project uses multiple tools to ensure code quality:

1. **Black** - Code formatting
2. **isort** - Import sorting
3. **Ruff** - Linting (replaces flake8, pylint)
4. **mypy** - Type checking
5. **Bandit** - Security scanning
6. **Safety** - Dependency vulnerability scanning

### Running Quality Checks

```bash
# Run all quality checks
make check

# Format code
make format

# Check formatting without changes
make format-check

# Run linting
make lint

# Run security checks
make security
```

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Build and Test (`build-and-test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- `test`: Runs all quality checks and tests
- `integration-test`: Runs integration tests for PRs
- `quality-gate`: Enforces quality standards

**Quality Gates:**
- ✅ Code formatting (Black)
- ✅ Import sorting (isort)
- ✅ Linting (Ruff)
- ✅ Type checking (mypy) - warning only
- ✅ Security scanning (Bandit)
- ✅ Unit tests with ≥80% coverage
- ✅ API endpoint tests
- ✅ Dependency vulnerability check

#### 2. Quality Gate (`quality-gate.yml`)

**Enhanced PR validation:**
- Enforces conventional commits
- Validates PR titles and descriptions
- Runs comprehensive quality checks
- Provides detailed feedback on failures

### Branch Protection

The CI pipeline is designed to block merges when:

1. **Tests fail** - Any test failure blocks merge
2. **Coverage drops** - Below 80% coverage threshold
3. **Linting fails** - Code quality issues detected
4. **Security issues** - Vulnerabilities found
5. **Formatting issues** - Code not properly formatted

### Failure Handling

When CI fails:

1. **Automatic Comments** - PR receives detailed feedback
2. **Clear Error Messages** - Specific instructions for fixes
3. **Artifact Upload** - Test reports and coverage data saved
4. **No Merge Allowed** - GitHub prevents merging until fixed

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
  # ... and more
```

Install hooks:
```bash
poetry run pre-commit install
```

## Test Structure

### Unit Tests (`test_plan_engine.py`)

```python
class TestPlanEngine:
    @pytest.fixture
    def plan_engine(self):
        return PlanEngine()
    
    def test_generate_plan_returns_dict(self, plan_engine):
        # Test implementation
        pass
```

### API Tests (`test_api.py`)

```python
class TestAPIEndpoints:
    @pytest_asyncio.fixture
    async def async_client(self, app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    async def test_health_check_endpoint_async(self, async_client):
        # Test implementation
        pass
```

## Coverage Reports

Coverage reports are generated in multiple formats:

1. **Terminal Output** - Summary during test runs
2. **HTML Report** - Detailed interactive report in `htmlcov/`
3. **XML Report** - For CI integration (`coverage.xml`)
4. **Codecov Integration** - Automatic upload to Codecov

## Best Practices

### Writing Tests

1. **Use descriptive test names** - Clearly indicate what is being tested
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **Use fixtures** - Share common setup between tests
4. **Test edge cases** - Including error conditions
5. **Mock external dependencies** - Keep tests isolated

### Maintaining Quality

1. **Run tests before committing** - Use pre-commit hooks
2. **Keep coverage high** - Aim for >80% coverage
3. **Fix issues immediately** - Don't let technical debt accumulate
4. **Review test failures** - Understand why tests fail
5. **Update tests with code changes** - Keep tests in sync

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Solution: Check PYTHONPATH and ensure modules are properly installed
   poetry install --with dev
   ```

2. **Async Test Failures**
   ```bash
   # Solution: Ensure pytest-asyncio is installed
   poetry add --group dev pytest-asyncio
   ```

3. **Coverage Issues**
   ```bash
   # Solution: Check coverage configuration and excluded files
   poetry run coverage report --show-missing
   ```

4. **Pre-commit Hook Failures**
   ```bash
   # Solution: Run formatting tools manually
   make format
   make check
   ```

### Debug Commands

```bash
# Run tests with verbose output
poetry run pytest -v --tb=long

# Run specific test with debugging
poetry run pytest tests/test_api.py::TestAPIEndpoints::test_health_check_endpoint_async -v -s

# Check test discovery
poetry run pytest --collect-only

# Run tests without coverage
poetry run pytest tests/ --no-cov
```

## Future Enhancements

- [ ] Performance testing with `pytest-benchmark`
- [ ] Load testing for API endpoints
- [ ] Contract testing with Pact
- [ ] Visual regression testing
- [ ] Database integration tests
- [ ] End-to-end testing with Playwright
