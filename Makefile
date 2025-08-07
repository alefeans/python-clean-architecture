.PHONY: help deps fmt unit-tests integration-tests all-tests staticcheck verify start stop watch-tests watch-unit-tests watch-integration-tests docker-up docker-up-dev docker-down docker-build docker-build-dev lint commit-check coverage clean pre-commit-install pre-commit-run
.DEFAULT_GOAL := help
GIT_HASH := $(shell git rev-parse HEAD)

define green_print
	@echo "\033[32m$1\033[0m"
endef

help:
	$(call green_print, "Usage:")
	@echo "  make [target]"
	@echo ""
	$(call green_print, "Targets:")
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[32m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

deps: ## Install dependencies
	$(call green_print, "Installing dependencies...")
	poetry install

fmt: ## Format all Python code
	$(call green_print, "Formatting all Python code...")
	ruff format app tests/

lint: ## Run linting checks
	$(call green_print, "Running linting checks...")
	ruff check app tests/

staticcheck: ## Run mypy for static analysis
	$(call green_print, "Running mypy...")
	mypy app/

unit-tests: ## Run unit tests
	$(call green_print, "Running unit tests...")
	pytest tests/unit/ -v

integration-tests: ## Run integration tests
	$(call green_print, "Running integration tests...")
	pytest tests/integration/ -v

all-tests: ## Run all tests
	$(call green_print, "Running all tests...")
	pytest tests/ -v

watch-tests: ## Run watch mode for all tests
	$(call green_print, "Running tests in watch mode...")
	pytest-watch tests/ -- -v

watch-unit-tests: ## Run watch mode for unit tests
	$(call green_print, "Running unit tests in watch mode...")
	pytest-watch tests/unit/ -- -v

watch-integration-tests: ## Run watch mode for integration tests
	$(call green_print, "Running integration tests in watch mode...")
	pytest-watch tests/integration/ -- -v

coverage: ## Run tests with coverage report
	$(call green_print, "Running tests with coverage...")
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v

pre-commit-install: ## Install pre-commit hooks
	$(call green_print, "Installing pre-commit hooks...")
	@which pre-commit > /dev/null 2>&1 && pre-commit install || python3 -m pre_commit install
	@which pre-commit > /dev/null 2>&1 && pre-commit install --hook-type commit-msg || python3 -m pre_commit install --hook-type commit-msg

pre-commit-run: ## Run pre-commit hooks on all files
	$(call green_print, "Running pre-commit hooks...")
	@which pre-commit > /dev/null 2>&1 && pre-commit run --all-files || python3 -m pre_commit run --all-files

commit-check: pre-commit-run ## Run pre-commit style checks
	$(call green_print, "Running commit checks...")
	@echo "All checks passed!"

clean: ## Clean up generated files
	$(call green_print, "Cleaning up...")
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

verify: deps lint staticcheck all-tests ## Verify the project by running tests and linters

start: ## Start the application
	$(call green_print, "Starting application...")
	poetry run python -m app

docker-build: ## Build Docker images
	$(call green_print, "Building Docker images...")
	docker compose build

docker-build-dev: ## Build development Docker image
	$(call green_print, "Building development Docker image...")
	docker compose build dev-base

docker-up: ## Start docker services (production)
	$(call green_print, "Starting Docker services (production)...")
	docker compose up app pg-db -d

docker-up-dev: ## Start docker services (development with hot reload)
	$(call green_print, "Starting Docker services (development)...")
	docker compose up app-dev pg-db -d

docker-down: ## Stop docker services
	$(call green_print, "Stopping Docker services...")
	docker compose down

stop: docker-down ## Stop all services
