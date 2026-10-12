# 47log-backend

47log のバックエンドリポジトリです。

## 開発用コマンド

コミット前には、次のコマンドで変更を加えない検証をまとめて実行します。

```bash
make check
```

pre-commit も Makefile の各ターゲットを呼び出し、`make check` と同じ項目を検証します。
各チェックを個別の hook に分けているため、失敗した項目を確認できます。

| コマンド | 説明 |
| --- | --- |
| `make lint` | Ruff による lint チェックを実行します。 |
| `make lint-fix` | Ruff による lint チェックを行い矯正します。 |
| `make format` | Ruff でコードを整形します。 |
| `make format-check` | Ruff の整形が適用済みかを確認します。 |
| `make typecheck` | Pyright による型チェックを実行します。 |
| `make imports` | import-linter によりアーキテクチャ上の import 契約を検証します。 |
| `make complexity` | 循環的複雑度が 10 を超える関数を検出します。 |
| `make test` | pytest と `src` のカバレッジ計測を実行します。 |
| `make test-integration` | DynamoDB Local を利用する統合テストを実行します。事前に `make dynamodb-up` が必要です。 |
| `make check` | lint、整形、型、import、複雑度、テストの検証をまとめて実行します。 |

## ローカル DynamoDB

| コマンド | 説明 |
| --- | --- |
| `make dynamodb-up` | Docker Compose で DynamoDB を起動し、初期化します。 |
| `make dynamodb-down` | DynamoDB を停止し、Docker ボリュームを削除します。 |

## Lambdaイメージのデプロイ

AWS CLIの認証とDockerを用意し、作成済みECRのURL（タグなし）とLambda関数名を指定します。

```bash
make develop-deploy \
  ECR_REPOSITORY_URL=123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/47log-backend \
  LAMBDA_FUNCTION_NAME=47log-development-api
```

ECRへのログイン、イメージのビルド・push、Lambdaのイメージ更新、更新完了の待機を順に実行します。
`IMAGE_TAG`は省略するとUTC日時から生成します。指定する場合は`IMAGE_TAG=<新しいタグ>`を追加してください。
リージョンは`AWS_REGION=ap-northeast-1`、ビルド対象は`PLATFORM=linux/amd64`が既定値です。
Lambdaが`arm64`なら`PLATFORM=linux/arm64`を指定してください。
認証に使うプロファイルは`AWS_PROFILE=<プロファイル名>`で選択できます。
デプロイする認証主体にはECRへのpushと対象Lambdaの`lambda:UpdateFunctionCode`・`lambda:GetFunction`が必要です。

## developmentのTerraform

`terraform/development`からAWSの開発環境を作成できます。stateはローカルに保存し、backend・databaseを管理します。LambdaのイメージURIは既存ECRから指定します。
設定と初回作成の手順は[開発環境のREADME](terraform/development/README.md)を参照してください。
`make develop`で、開発環境のTerraformの`init -lockfile=readonly`と`apply --auto-approve`を順に実行し、承認入力なしで変更を適用します。
`make develop-destroy`で、開発環境のTerraformの`init`と`destroy -auto-approve`を順に実行し、管理対象のリソースを削除します。

## productionのTerraform

`terraform/production/main.tf`から[47log-infraのbackend](https://github.com/yuta15/47log-infra/tree/main/terraform/modules/backend)と[database](https://github.com/yuta15/47log-infra/tree/main/terraform/modules/database)をGit source（`ref=main`）で読み込みます。
JWT認証付きHTTP API、コンテナLambda、ユーザー・訪問記録用DynamoDBテーブルを管理します。
テーブル名は`${project_name}-users`と`${project_name}-visits`です。
Lambdaへ`USERS_TABLE_NAME`と`VISIT_TABLE_NAME`を渡し、両テーブルへのアクセス権限を設定します。
現在のLambdaハンドラーはユーザー管理ルートを登録しています。訪問記録APIのルート追加は別途必要です。

`terraform/production/terraform.tfvars.example`を`terraform.tfvars`にコピーし、push済みのECRイメージURI、既存Cognitoのissuer・アプリクライアントID、フロントエンドのoriginを設定してください。
イメージにはLambda Runtime Interface Clientと`src.functions.handler.handler`を呼び出す設定が必要です。
Cognito、ECR、Terraform state用S3バケットは事前に用意します。

```bash
terraform -chdir=terraform/production init \
  -backend-config="bucket=<state用S3バケット>" \
  -backend-config="key=47log-backend/production/terraform.tfstate" \
  -backend-config="region=ap-northeast-1"
terraform -chdir=terraform/production plan
terraform -chdir=terraform/production apply
```

backendモジュールは初回作成後の`image_uri`変更を無視するため、以降のイメージ更新はCI/CDなどから行います。
関数名は`terraform output lambda_function_names`で確認できます。
モジュールを更新するときは`terraform init -upgrade`を実行します。
productionで参照バージョンを固定する場合は、両moduleの`ref=main`を同じタグまたはコミットSHAに置き換えてください。
