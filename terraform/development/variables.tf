variable "aws_region" {
  description = "developmentをデプロイするAWSリージョン。"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "developmentのリソース名の接頭辞。"
  type        = string
  default     = "47log-development"
}

variable "backend_initial_image_uri" {
  description = "既存ECRへpush済みのLambda初回作成用イメージURI。タグまたはdigestを含める。"
  type        = string
  nullable    = false
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
