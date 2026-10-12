# 47log-backend

47log のバックエンドリポジトリです。

## 開発用コマンド

コミット前は`make check`で検証します。pre-commitも同じ項目を実行します。

| コマンド | 説明 |
| --- | --- |
| `make check` | lint・整形・型・依存・複雑度・単体テストを検証 |
| `make lint` / `make lint-fix` | Ruffのlint / 自動修正 |
| `make format` / `make format-check` | 整形 / 整形チェック |
| `make typecheck` | Pyrightの型チェック |
| `make imports` | importの依存ルールを検証 |
| `make complexity` | 循環的複雑度10超を検出 |
| `make test` | 単体テストとカバレッジ計測 |
| `make test-integration` | 統合テスト（DynamoDB Localの起動が必要） |

## ローカル DynamoDB

| コマンド | 説明 |
| --- | --- |
| `make dynamodb-up` | 起動・テーブル初期化 |
| `make dynamodb-down` | 停止・データ削除 |

## AWS開発環境

| コマンド | 説明 |
| --- | --- |
| `make develop` | Terraform apply（自動承認） |
| `make develop-destroy` | Terraform destroy（自動承認） |
| `make develop-deploy` | イメージのビルド・ECRへpush・Lambda更新 |

設定と手順は[開発環境のREADME](terraform/development/README.md)を参照してください。
