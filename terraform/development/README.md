# AWS開発環境

47log-infraのbackend・databaseモジュールでHTTP API、Lambda、DynamoDBを作成します。
stateはこのディレクトリの`terraform.tfstate`に保存します。

## 初回作成

事前に47log-infraのTerraformを実行し、Lambdaと同じリージョンのECRへLambda対応のdummy imageをpushしてください。
以下はAWS認証を設定し、リポジトリルートから実行します。

```bash
cp terraform/development/terraform.tfvars.example terraform/development/terraform.tfvars
```

`terraform.tfvars`にpush済みの`backend_initial_image_uri`、Cognito設定、CORSのoriginを指定します。
`backend_architecture`はイメージのCPUアーキテクチャと合わせてください。

```bash
make develop
```

`init -lockfile=readonly`と`apply --auto-approve`を実行します。
stateと`terraform.tfvars`はGit管理対象外です。stateは継続して保持してください。

## イメージ更新

```bash
make develop-deploy \
  ECR_REPOSITORY_URL=<タグなしのECR URL> \
  LAMBDA_FUNCTION_NAME=47log-development-api
```

Dockerfileでビルド・pushし、Lambdaの更新完了まで待機します。
既定値は`AWS_REGION=ap-northeast-1`、`PLATFORM=linux/amd64`、`IMAGE_TAG`はUTC日時です。
Lambdaが`arm64`なら`PLATFORM=linux/arm64`を指定してください。
Terraformは初回作成後の`image_uri`変更を無視します。初回用イメージは再作成に使うためECRに保持してください。

## 削除

```bash
make develop-destroy
```

`init -lockfile=readonly`と`destroy -auto-approve`を実行します。
