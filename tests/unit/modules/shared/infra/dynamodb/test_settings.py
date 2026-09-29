"""DynamoDB 接続設定のテスト。"""

from src.modules.shared.infra.dynamodb import DynamoDBSettings


def test_dynamodb_settings_uses_default_region_without_environment_values(
    monkeypatch,
) -> None:
    """環境変数がない場合にデフォルト設定が使われることを確認する。"""
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("DYNAMODB_ENDPOINT_URL", raising=False)

    assert DynamoDBSettings(
        region_name="ap-northeast-1",
        endpoint_url=None,
    )


def test_dynamodb_settings_reads_environment_values(monkeypatch) -> None:
    """環境変数で DynamoDB 接続設定を上書きできることを確認する。"""
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")

    assert DynamoDBSettings() == DynamoDBSettings(
        region_name="us-east-1", endpoint_url="http://localhost:8000"
    )
