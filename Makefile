.PHONY: dynamodb-up dynamodb-down

dynamodb-up:
	docker compose up -d dynamodb-init

dynamodb-down:
	docker compose down --volumes
