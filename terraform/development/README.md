# AWS開発環境

ローカルのTerraformからAWSへJWT認証付きHTTP API、コンテナLambda、DynamoDBテーブルを作成します。
backend・databaseはproductionと同じ47log-infraのモジュール（`ref=main`）を使います。
既定の接頭辞は`47log-development`、テーブル名は`47log-development-users`と`47log-development-visits`です。
stateはこのディレクトリの`terraform.tfstate`に保存されます。

## 初回作成

事前に47log-infraのTerraformを実行し、開発用Cognito User Pool・アプリクライアントなどの基盤を作成してください。
Lambdaと同じリージョンの既存ECRへ、Lambda初回作成用のdummy imageをpush済みの状態で`plan`・`apply`を実行してください。
イメージURIは`backend_initial_image_uri`で受け取ります（例: `123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/47log-backend:initial`）。

以下はこのリポジトリのルートから、AWS認証を設定した状態で実行します。
`terraform.tfvars.example`を`terraform.tfvars`へコピーし、push済みイメージのURI・Cognito設定・CORSのoriginを実際の値に変更します。

```bash
cp terraform/development/terraform.tfvars.example terraform/development/terraform.tfvars
terraform -chdir=terraform/development init
```

dummy imageのCPUアーキテクチャを`backend_architecture`に合わせ、Lambdaで実行できるイメージを使用してください。
実際のバックエンドイメージにはLambda Runtime Interface Clientと`src.functions.handler.handler`を呼び出す設定を含めてください。
リポジトリルートのDockerfileで、`uv.lock`の実行用依存とハンドラーを含むイメージをビルドできます。
`backend_architecture = "x86_64"`の場合は次のコマンドを使います。`arm64`の場合は`--platform linux/arm64`へ変更してください。

```bash
docker buildx build --platform linux/amd64 --provenance=false --load -t 47log-backend:dev .
```

```bash
terraform -chdir=terraform/development plan
terraform -chdir=terraform/development apply
```

リポジトリルートで`make develop`を実行すると、`init -lockfile=readonly`と`apply --auto-approve`を順に実行します。
`make develop`は承認入力なしで変更を適用します。

初回用イメージは再作成にも使うため、ECRに保持してください。
更新時は新しいタグまたはdigestのイメージを用意し、CI/CD等でLambdaのコードを更新します。
backendモジュールは初回作成後の`image_uri`変更を無視します。
実際のバックエンドへの切り替えには、リポジトリルートで`make develop-deploy ECR_REPOSITORY_URL=<タグなしのECR URL> LAMBDA_FUNCTION_NAME=<関数名>`を実行します。
Lambda関数名は`terraform -chdir=terraform/development output lambda_function_names`で確認できます。

通常の変更にはターゲットを指定せず`plan`・`apply`を実行します。
stateと`terraform.tfvars`はGitの管理対象外です。ローカルstateを保持して同じ環境を管理してください。

開発環境の削除は`make develop-destroy`で実行します。`init`の後、`destroy -auto-approve`で管理対象のリソースを確認なしで削除します。
