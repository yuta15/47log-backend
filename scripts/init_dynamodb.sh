#!/bin/sh

set -eu

endpoint_url="${DYNAMODB_ENDPOINT_URL:-http://dynamodb-local:8000}"

table_exists() {
  aws dynamodb describe-table \
    --table-name "$1" \
    --endpoint-url "$endpoint_url" \
    >/dev/null 2>&1
}

create_users_table() {
  aws dynamodb create-table \
    --table-name users_table \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$endpoint_url"
}

create_visit_table() {
  aws dynamodb create-table \
    --table-name visit_table \
    --attribute-definitions \
      AttributeName=user_id,AttributeType=S \
      AttributeName=visit_id,AttributeType=S \
    --key-schema \
      AttributeName=user_id,KeyType=HASH \
      AttributeName=visit_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$endpoint_url"
}

if table_exists users_table; then
  echo "users_table already exists"
else
  echo "Creating users_table"
  create_users_table
fi

if table_exists visit_table; then
  echo "visit_table already exists"
else
  echo "Creating visit_table"
  create_visit_table
fi
