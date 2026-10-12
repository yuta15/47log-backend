output "api_endpoint" {
  description = "HTTP APIのエンドポイント。"
  value       = module.backend.api_endpoint
}

output "lambda_function_names" {
  description = "CI/CDでイメージを更新するLambda関数名。"
  value       = module.backend.lambda_function_names
}

output "table_arns" {
  description = "DynamoDBテーブル名をキーとするARNマップ。"
  value       = module.database.table_arns
}
