"""DynamoDBContext のテスト。"""

from unittest.mock import sentinel

from src.modules.shared.infra.dynamodb import DynamoDBContext, DynamoDBSettings


def test_dynamodb_context_uses_the_provided_settings(monkeypatch) -> None:
    """設定値を使用して resource が生成されることを確認する。"""
    captured_arguments: dict[str, object] = {}

    def fake_resource(service_name: str, **kwargs: object) -> object:
        captured_arguments["service_name"] = service_name
        captured_arguments.update(kwargs)
        return sentinel.resource

    monkeypatch.setattr("boto3.resource", fake_resource)

    settings = DynamoDBSettings(
        region_name="ap-northeast-1",
        endpoint_url="http://localhost:8000",
    )

    context = DynamoDBContext(settings)

    assert context.settings is settings
    assert context.resource is sentinel.resource
    assert captured_arguments == {
        "service_name": "dynamodb",
        "region_name": "ap-northeast-1",
        "endpoint_url": "http://localhost:8000",
    }
