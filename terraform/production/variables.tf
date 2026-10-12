variable "aws_region" {
  description = "productionをデプロイするAWSリージョン。"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "productionのリソース名の接頭辞。"
  type        = string
  default     = "47log-production"
}

variable "backend_initial_image_uri" {
  description = "Lambda初回作成用のECRイメージURI。同じリージョンに事前にpushする。"
  type        = string
}

variable "backend_architecture" {
  description = "LambdaコンテナイメージのCPUアーキテクチャ。"
  type        = string
  default     = "x86_64"
}

variable "jwt_authorizer" {
  description = "既存Cognito User Poolのissuer URLとアプリクライアントID。"
  type = object({
    issuer   = string
    audience = set(string)
  })
  nullable = false
}

variable "cors_allow_origins" {
  description = "CORSを許可するフロントエンドのorigin。空集合の場合はCORSを無効にする。"
  type        = set(string)
  default     = []
  nullable    = false
}
