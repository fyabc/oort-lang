.PHONY: help install dev test benchmark benchmark-json lint format format-check type-check imports security audit deps dead-code property markdown quality clean build-grammar check

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

benchmark-json: ## Run benchmarks and write benchmark.json
	uv run pytest benchmarks/ --benchmark-json=benchmark.json -q

lint: ## Run linters
	uv run ruff check src/ tests/ benchmarks/ scripts/

format: ## Format code
	uv run ruff format src/ tests/ benchmarks/ scripts/

format-check: ## Check formatting without modifying files
	uv run ruff format --check src/ tests/ benchmarks/ scripts/

type-check: ## Run type checking
	uv run mypy src/

imports: ## Check module import boundaries
	uv run --with "import-linter>=2" lint-imports

security: ## Run bandit security scan
	uv run --with bandit bandit -c pyproject.toml -r src/oort_lang -q

audit: ## Audit installed dependencies for known vulnerabilities
	uv run --with pip-audit pip-audit

deps: ## Check dependency hygiene
	uv run --with deptry deptry .

dead-code: ## Find unused code
	uv run --with vulture vulture src/oort_lang --exclude src/oort_lang/parser/grammar --min-confidence 80

property: ## Run property-based tests
	uv run --with hypothesis pytest tests/property -q

markdown: ## Lint Markdown documents
	npx --yes markdownlint-cli2@0.18.1 "README.md" "CONTRIBUTING.md" "docs/**/*.md" "benchmarks/README.md" "tests/README.md"

quality: security audit deps dead-code property markdown ## Run optional quality/security gates

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

check: lint format-check type-check imports test ## Run all checks (non-mutating)
