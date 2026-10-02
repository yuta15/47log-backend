"""DynamoDBVisitRepository の単体テスト。"""

from dataclasses import replace
from decimal import Decimal
from uuid import UUID

import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError, EndpointConnectionError

from src.modules.visit_management.application import (
    VisitAlreadyExistsError,
    VisitNotFoundError,
    VisitRepositoryError,
)
from src.modules.visit_management.domain import Prefecture, Visit


@pytest.mark.parametrize("prefecture_id", [1, 47])
def test_list_visits_success_returns_mapped_visits(
    repository, table, visit: Visit, prefecture_id: int
) -> None:
    """DynamoDB が指定ユーザーの訪問記録を返した場合の変換を確認する。

    list_visits の戻り値が、取得した記録と同じ値を持つ Visit のリストになること。
    各 Visit の user_id が str、visit_id が UUID、created_at が datetime になること。
    prefecture_id が 1 または 47 の場合、prefecture が対応する Prefecture になること。
    Query の検索条件が指定した user_id との一致条件で、取得順が昇順になること。
    """
    # Arrange
    expected_visit = replace(visit, prefecture=Prefecture(prefecture_id))
    table.query.return_value = {
        "Items": [
            {
                "user_id": visit.user_id,
                "visit_id": str(visit.visit_id),
                "prefecture_id": Decimal(prefecture_id),
                "created_at": visit.created_at.isoformat(),
            }
        ]
    }

    # Act
    actual_visits = repository.list_visits(visit.user_id)

    # Assert
    assert actual_visits == [expected_visit]
    assert actual_visits[0].prefecture is expected_visit.prefecture
    table.query.assert_called_once()
    arguments = table.query.call_args.kwargs
    assert arguments["KeyConditionExpression"] == Key("user_id").eq(visit.user_id)
    assert arguments.get("ScanIndexForward", True) is True


@pytest.mark.parametrize("response", [{}, {"Items": []}])
def test_list_visits_success_returns_empty_list_when_no_visits_exist(
    repository, table, user_id: str, response: dict
) -> None:
    """DynamoDB の応答に Items がない場合、または Items が空の場合を確認する。

    list_visits の戻り値が空リストになること。
    """
    # Arrange
    table.query.return_value = response

    # Act
    actual_visits = repository.list_visits(user_id)

    # Assert
    assert actual_visits == []


def test_list_visits_success_reads_all_pages(repository, table, visit: Visit) -> None:
    """DynamoDB が訪問記録を2ページに分けて返す場合の一覧取得を確認する。

    list_visits が1ページ目の LastEvaluatedKey を
    2ページ目の Query の ExclusiveStartKey に指定すること。
    2ページ目の検索条件も、1ページ目と同じ user_id の一致条件になること。
    list_visits の戻り値が、両ページの Visit を順番に含むリストになること。
    """
    # Arrange
    second_visit = replace(visit, visit_id=UUID("019994f0-0000-7000-8000-000000000002"))
    last_key = {"user_id": visit.user_id, "visit_id": str(visit.visit_id)}
    table.query.side_effect = [
        {
            "Items": [
                {
                    **last_key,
                    "prefecture_id": Decimal(visit.prefecture.value),
                    "created_at": visit.created_at.isoformat(),
                }
            ],
            "LastEvaluatedKey": last_key,
        },
        {
            "Items": [
                {
                    "user_id": second_visit.user_id,
                    "visit_id": str(second_visit.visit_id),
                    "prefecture_id": Decimal(second_visit.prefecture.value),
                    "created_at": second_visit.created_at.isoformat(),
                }
            ]
        },
    ]

    # Act
    actual_visits = repository.list_visits(visit.user_id)

    # Assert
    assert actual_visits == [visit, second_visit]
    assert table.query.call_count == 2
    first_arguments, second_arguments = [
        call.kwargs for call in table.query.call_args_list
    ]
    assert "ExclusiveStartKey" not in first_arguments
    assert second_arguments["ExclusiveStartKey"] == last_key
    assert (
        second_arguments["KeyConditionExpression"]
        == first_arguments["KeyConditionExpression"]
    )


@pytest.mark.parametrize("prefecture_id", [1, 47])
def test_create_visit_success_writes_a_mapped_item(
    repository, table, visit: Visit, prefecture_id: int
) -> None:
    """create_visit に Visit を渡した場合の書込み内容を確認する。

    Item の user_id は元の文字列を保持し、visit_id は UUID の文字列になること。
    Item の created_at が Visit の作成日時を表す ISO 8601 形式の文字列になること。
    Visit の prefecture が北海道の場合、Item の prefecture_id が 1 になること。
    Visit の prefecture が沖縄の場合、Item の prefecture_id が 47 になること。
    """
    # Arrange
    visit = replace(visit, prefecture=Prefecture(prefecture_id))

    # Act
    repository.create_visit(visit)

    # Assert
    table.put_item.assert_called_once()
    assert table.put_item.call_args.kwargs["Item"] == {
        "user_id": visit.user_id,
        "visit_id": str(visit.visit_id),
        "prefecture_id": prefecture_id,
        "created_at": visit.created_at.isoformat(),
    }


def test_create_visit_failure_raises_when_visit_already_exists(
    repository, table, visit: Visit, conditional_check_failed_exception
) -> None:
    """DynamoDB が複合キー重複による条件付き作成の失敗を返す場合を確認する。

    create_visit が VisitAlreadyExistsError を送出すること。
    送出した例外の __cause__ が、DynamoDB から受け取った例外になること。
    """
    # Arrange
    error = conditional_check_failed_exception()
    table.put_item.side_effect = error

    # Assert
    with pytest.raises(VisitAlreadyExistsError) as raised:
        repository.create_visit(visit)
    assert raised.value.__cause__ is error


def test_delete_visit_success_deletes_by_composite_key(
    repository, table, visit: Visit
) -> None:
    """delete_visit に user_id と visit_id を渡した場合の削除キーを確認する。

    Key の user_id は元の文字列を保持し、visit_id は指定した UUID の文字列になること。
    """
    # Act
    repository.delete_visit(visit.user_id, visit.visit_id)

    # Assert
    table.delete_item.assert_called_once()
    assert table.delete_item.call_args.kwargs["Key"] == {
        "user_id": visit.user_id,
        "visit_id": str(visit.visit_id),
    }


def test_delete_visit_failure_raises_when_visit_does_not_exist(
    repository, table, visit: Visit, conditional_check_failed_exception
) -> None:
    """DynamoDB が対象記録の不在による条件付き削除の失敗を返す場合を確認する。

    delete_visit が VisitNotFoundError を送出すること。
    送出した例外の __cause__ が、DynamoDB から受け取った例外になること。
    """
    # Arrange
    error = conditional_check_failed_exception()
    table.delete_item.side_effect = error

    # Assert
    with pytest.raises(VisitNotFoundError) as raised:
        repository.delete_visit(visit.user_id, visit.visit_id)
    assert raised.value.__cause__ is error


@pytest.mark.parametrize(
    ("method_name", "table_method", "operation"),
    [
        ("list_visits", "query", "Query"),
        ("create_visit", "put_item", "PutItem"),
        ("delete_visit", "delete_item", "DeleteItem"),
    ],
)
@pytest.mark.parametrize("error_kind", ["service", "connection"])
def test_repository_failure_wraps_dynamodb_errors(
    repository,
    table,
    visit: Visit,
    method_name: str,
    table_method: str,
    operation: str,
    error_kind: str,
) -> None:
    """DynamoDB が各操作でサービスエラーまたは接続障害を返す場合を確認する。

    呼び出したメソッド (list_visits・create_visit・delete_visit) が
    VisitRepositoryError を送出すること。
    送出した例外の __cause__ が、DynamoDB から受け取った例外になること。
    """
    # Arrange
    error = (
        ClientError({"Error": {"Code": "AccessDeniedException"}}, operation)
        if error_kind == "service"
        else EndpointConnectionError(endpoint_url="http://localhost:8000")
    )
    getattr(table, table_method).side_effect = error
    arguments = {
        "list_visits": (visit.user_id,),
        "create_visit": (visit,),
        "delete_visit": (visit.user_id, visit.visit_id),
    }[method_name]

    # Assert
    with pytest.raises(VisitRepositoryError) as raised:
        getattr(repository, method_name)(*arguments)
    assert raised.value.__cause__ is error
