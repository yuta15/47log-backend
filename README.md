# 47log-backend

47log のバックエンドリポジトリです。

## API

API Gateway HTTP API の payload v2 を Powertools で処理します。
Lambda のハンドラーは `src.functions.handler.handler` に設定します。
API Gateway の統合では `payload_format_version` を `2.0` に設定し、
認証が必要なルートに JWT Authorizer を設定します。

現在のエンドポイントは `GET /users/me` です。
JWT Authorizer の `sub` からユーザーを特定し、
`accountName`、`createdAt`、`updatedAt`、`status` を JSON で返します。

エンドポイントの処理、依存生成、レスポンスモデルは
`src/functions/<module>/<endpoint>/` に配置します。
モジュールの `router.py` で共有 Router を定義し、
各 `endpoint.py` のデコレーターでメソッド・パスを登録します。
モジュールの `__init__.py` でエンドポイントを読み込み、Router を公開します。
`handler.py` の Resolver にモジュールの Router を登録します。
認証情報の取得・検証は `src/functions/auth/` に配置します。

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
