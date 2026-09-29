.PHONY: check complexity dynamodb-down dynamodb-up format format-check imports lint test test-integration typecheck

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run pyright

imports:
	uv run lint-imports

test:
	uv run pytest

test-integration:
	uv run pytest tests/integration

complexity:
	uv run ruff check --select C901 src

check: lint format-check typecheck imports complexity test

dynamodb-up:
	docker compose up -d dynamodb-init

dynamodb-down:
	docker compose down --volumes
