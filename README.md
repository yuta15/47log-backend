# 47log-backend

47log のバックエンドリポジトリです。

## 開発用コマンド

コミット前の検証は`make check`で実行します。

pre-commitでも同じ項目を検証します。

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

## AWS開発環境

| コマンド | 説明 |
| --- | --- |
| `make develop` | Terraformで開発環境を作成・更新します（自動承認）。 |
| `make develop-destroy` | Terraformで開発環境を削除します（自動承認）。 |
| `make develop-deploy` | イメージをビルドしてECRへpushし、Lambdaを更新します。 |

事前設定と実行手順は[開発環境のREADME](terraform/development/README.md)を参照してください。
