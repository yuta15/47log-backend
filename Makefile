.PHONY: check develop-deploy complexity develop-destroy dynamodb-down dynamodb-up format format-check imports lint lint-fix develop test test-integration typecheck

AWS_REGION ?= ap-northeast-1
ECR_REPOSITORY_URL ?=
LAMBDA_FUNCTION_NAME ?=
IMAGE_TAG ?=
PLATFORM ?= linux/amd64
export AWS_REGION ECR_REPOSITORY_URL LAMBDA_FUNCTION_NAME IMAGE_TAG PLATFORM

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

develop:
	terraform -chdir=terraform/development init -lockfile=readonly
	terraform -chdir=terraform/development apply --auto-approve

develop-destroy:
	terraform -chdir=terraform/development init -lockfile=readonly
	terraform -chdir=terraform/development destroy -auto-approve

develop-deploy: SHELL := /bin/bash
develop-deploy:
	@set -euo pipefail; \
	: "$${ECR_REPOSITORY_URL:?ECR_REPOSITORY_URLを指定してください（タグなし）}"; \
	: "$${LAMBDA_FUNCTION_NAME:?LAMBDA_FUNCTION_NAMEを指定してください}"; \
	image_tag="$${IMAGE_TAG:-$$(date -u +%Y%m%dT%H%M%SZ)}"; \
	image_uri="$${ECR_REPOSITORY_URL}:$${image_tag}"; \
	registry="$${ECR_REPOSITORY_URL%%/*}"; \
	aws ecr get-login-password --region "$$AWS_REGION" \
		| docker login --username AWS --password-stdin "$$registry"; \
	docker buildx build --platform "$$PLATFORM" --provenance=false \
		--push -t "$$image_uri" .; \
	aws lambda update-function-code --region "$$AWS_REGION" \
		--function-name "$$LAMBDA_FUNCTION_NAME" --image-uri "$$image_uri" \
		--query FunctionName --output text --no-cli-pager; \
	aws lambda wait function-updated-v2 --region "$$AWS_REGION" \
		--function-name "$$LAMBDA_FUNCTION_NAME"; \
	printf 'Lambdaのイメージを更新しました: %s\n' "$$image_uri"
