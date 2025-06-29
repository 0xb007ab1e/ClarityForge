.PHONY: help install test test-unit test-api test-integration test-all lint format check clean coverage
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using Poetry
	poetry install --with dev

test: test-unit test-api ## Run all tests (unit and API)

test-unit: ## Run unit tests
	poetry run pytest tests/test_plan_engine.py -v --tb=short -m "not api"

test-api: ## Run API tests
	poetry run pytest tests/test_api.py -v --tb=short

test-integration: ## Run integration tests
	poetry run pytest tests/ -v --tb=short -m "integration"

test-all: ## Run all tests with coverage
	poetry run coverage run -m pytest tests/ -v --tb=short
	poetry run coverage report --show-missing
	poetry run coverage html

lint: ## Run linting checks
	poetry run ruff check .
	poetry run mypy clarity_forge/ --ignore-missing-imports

format: ## Format code with Black and isort
	poetry run black .
	poetry run isort .

format-check: ## Check code formatting without making changes
	poetry run black --check --diff .
	poetry run isort --check-only --diff .

security: ## Run security checks
	poetry run bandit -r clarity_forge/ -f screen
	poetry run safety check

check: format-check lint security ## Run all checks (formatting, linting, security)

coverage: ## Generate coverage report
	poetry run coverage run -m pytest tests/
	poetry run coverage report --show-missing --fail-under=80
	poetry run coverage html
	@echo "Coverage report generated in htmlcov/"

clean: ## Clean up generated files
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

dev-setup: install ## Setup development environment
	poetry run pre-commit install

ci: check test-all ## Run CI pipeline locally
	@echo "✅ All CI checks passed!"

docker-test: ## Run tests in Docker environment
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

watch-tests: ## Run tests in watch mode
	poetry run ptw tests/ --runner "poetry run pytest"
