"""訪問記録を DynamoDB に保存する Repository。"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import BotoCoreError, ClientError

from ...shared.infra.dynamodb import DynamoDBContext
from ..application import (
    VisitAlreadyExistsError,
    VisitNotFoundError,
    VisitRepository,
    VisitRepositoryError,
)
from ..domain import Prefecture, Visit


class DynamoDBVisitRepository(VisitRepository):
    """訪問記録をユーザー ID と訪問記録 ID の複合キーで管理する。"""

    def __init__(self, context: DynamoDBContext, *, table_name: str) -> None:
        """DynamoDB の接続情報と訪問記録のテーブル名を受け取る。"""
        resource = cast(Any, context.resource)
        self._table: Any = resource.Table(table_name)

    def list_visits(self, user_id: str) -> list[Visit]:
        """指定ユーザーの全訪問記録を visit_id の昇順で返す。"""
        arguments: dict[str, Any] = {
            "KeyConditionExpression": Key("user_id").eq(user_id),
            "ScanIndexForward": True,
            "ConsistentRead": True,
        }
        visits: list[Visit] = []
        try:
            while True:
                response = self._table.query(**arguments)
                visits.extend(
                    self._to_visit(item) for item in response.get("Items", [])
                )
                last_key = response.get("LastEvaluatedKey")
                if not last_key:
                    return visits
                arguments["ExclusiveStartKey"] = last_key
        except (BotoCoreError, ClientError) as error:
            raise VisitRepositoryError from error

    def create_visit(self, visit: Visit) -> None:
        """同じ複合キーの記録を上書きせずに訪問記録を作成する。"""
        conditional_check_failed = (
            self._table.meta.client.exceptions.ConditionalCheckFailedException
        )
        try:
            self._table.put_item(
                Item=self._to_item(visit),
                ConditionExpression=Attr("user_id").not_exists()
                & Attr("visit_id").not_exists(),
            )
        except conditional_check_failed as error:
            raise VisitAlreadyExistsError from error
        except (BotoCoreError, ClientError) as error:
            raise VisitRepositoryError from error

    def delete_visit(self, user_id: str, visit_id: UUID) -> None:
        """指定した複合キーの訪問記録を削除し、不在の場合は例外を送出する。"""
        conditional_check_failed = (
            self._table.meta.client.exceptions.ConditionalCheckFailedException
        )
        try:
            self._table.delete_item(
                Key={"user_id": user_id, "visit_id": str(visit_id)},
                ConditionExpression=Attr("user_id").exists()
                & Attr("visit_id").exists(),
            )
        except conditional_check_failed as error:
            raise VisitNotFoundError from error
        except (BotoCoreError, ClientError) as error:
            raise VisitRepositoryError from error

    @staticmethod
    def _to_item(visit: Visit) -> dict[str, str | int]:
        """Visit の各属性を DynamoDB に保存する値に変換する。"""
        return {
            "user_id": visit.user_id,
            "visit_id": str(visit.visit_id),
            "prefecture_id": visit.prefecture.value,
            "created_at": visit.created_at.isoformat(),
        }

    @staticmethod
    def _to_visit(item: Mapping[str, Any]) -> Visit:
        """user_id の文字列を保持し、他の属性を変換して Visit を返す。"""
        return Visit(
            user_id=item["user_id"],
            visit_id=UUID(str(item["visit_id"])),
            prefecture=Prefecture(item["prefecture_id"]),
            created_at=datetime.fromisoformat(str(item["created_at"])),
        )
