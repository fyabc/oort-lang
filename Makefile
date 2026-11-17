.PHONY: help install dev test benchmark lint format type-check clean build-grammar

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the project
	uv sync

dev: ## Install with development dependencies
	uv sync --extra dev

test: ## Run tests
	uv run pytest tests/ -v

benchmark: ## Run benchmarks
	uv run pytest benchmarks/ -v

lint: ## Run linters
	uv run ruff check src/ tests/ benchmarks/

format: ## Format code
	uv run ruff format src/ tests/ benchmarks/

type-check: ## Run type checking
	uv run mypy src/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build-grammar: ## Rebuild grammar files
	uv run python scripts/build_grammar.py

check: lint format type-check test ## Run all checks
