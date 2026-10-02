"""DynamoDBVisitRepository の統合テスト。"""

from dataclasses import replace

import pytest

from src.modules.visit_management.application import (
    VisitAlreadyExistsError,
    VisitNotFoundError,
)
from src.modules.visit_management.domain import Prefecture, Visit

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("prefecture_id", [1, 47])
def test_create_visit_success_persists_and_reads_visit(
    repository, visit: Visit, prefecture_id: int
) -> None:
    """create_visit で訪問記録を保存し、同じ user_id で一覧取得した結果を確認する。

    list_visits の戻り値が、保存した Visit だけを含むリストになること。
    取得した Visit の全属性が保存した値と一致すること。
    取得した Visit の prefecture が対応する Prefecture になること。
    """
    # Arrange
    visit = replace(visit, prefecture=Prefecture(prefecture_id))

    # Act
    repository.create_visit(visit)
    actual_visits = repository.list_visits(visit.user_id)

    # Assert
    assert actual_visits == [visit]
    assert actual_visits[0].prefecture is visit.prefecture


def test_list_visits_success_returns_empty_list_when_no_visits_exist(
    repository, visit: Visit
) -> None:
    """指定した user_id の訪問記録が DynamoDB に存在しない場合を確認する。

    list_visits の戻り値が空リストになること。
    """
    # Act
    actual_visits = repository.list_visits(visit.user_id)

    # Assert
    assert actual_visits == []


def test_list_visits_success_returns_visits_in_id_order(
    repository, visit: Visit, second_visit: Visit
) -> None:
    """同じユーザーの記録を visit_id の大きい順に2件保存した場合を確認する。

    list_visits の戻り値が、2件の Visit を visit_id の小さい順に含むリストになること。
    """
    # Arrange
    repository.create_visit(second_visit)
    repository.create_visit(visit)

    # Act
    actual_visits = repository.list_visits(visit.user_id)

    # Assert
    assert actual_visits == [visit, second_visit]


def test_list_visits_success_returns_only_requested_users_visits(
    repository, visit: Visit, other_user_visit: Visit
) -> None:
    """ユーザーAとBが同じ visit_id の記録をそれぞれ持つ場合を確認する。

    ユーザーAの user_id で呼び出した list_visits の戻り値が、Aの記録だけを含むこと。
    戻り値にユーザーBの記録が含まれないこと。
    """
    # Arrange
    repository.create_visit(visit)
    repository.create_visit(other_user_visit)

    # Act
    actual_visits = repository.list_visits(visit.user_id)

    # Assert
    assert actual_visits == [visit]


def test_create_visit_success_allows_same_prefecture_with_different_ids(
    repository, visit: Visit, second_visit: Visit
) -> None:
    """user_id・prefecture が同じで visit_id が異なる2件を作成する場合を確認する。

    create_visit が両方の記録を保存できること。
    list_visits の戻り値が、作成した2件の Visit を含むリストになること。
    """
    # Act
    repository.create_visit(visit)
    repository.create_visit(second_visit)

    # Assert
    assert repository.list_visits(visit.user_id) == [visit, second_visit]


def test_create_visit_failure_preserves_original_when_visit_already_exists(
    repository, visit: Visit
) -> None:
    """保存済みの記録と同じ user_id・visit_id で別の都道府県を登録する場合を確認する。

    create_visit が VisitAlreadyExistsError を送出すること。
    list_visits で取得した元の記録の全属性が、重複作成前の値と一致すること。
    """
    # Arrange
    repository.create_visit(visit)
    duplicate = replace(visit, prefecture=Prefecture.OKINAWA)

    # Assert
    with pytest.raises(VisitAlreadyExistsError):
        repository.create_visit(duplicate)
    assert repository.list_visits(visit.user_id) == [visit]


def test_delete_visit_success_preserves_other_visits(
    repository, visit: Visit, second_visit: Visit, other_user_visit: Visit
) -> None:
    """ユーザーAが2件、BがAの削除対象と同じ visit_id の記録を持つ場合を確認する。

    delete_visit にAの user_id と対象の visit_id を渡すと、対象の記録が削除されること。
    Aの一覧取得結果が、削除対象以外の1件だけを含むリストになること。
    Bの一覧取得結果が、削除前と同じ記録を含むリストになること。
    """
    # Arrange
    for record in (visit, second_visit, other_user_visit):
        repository.create_visit(record)

    # Act
    repository.delete_visit(visit.user_id, visit.visit_id)

    # Assert
    assert repository.list_visits(visit.user_id) == [second_visit]
    assert repository.list_visits(other_user_visit.user_id) == [other_user_visit]


@pytest.mark.parametrize("previously_deleted", [False, True])
def test_delete_visit_failure_raises_when_visit_does_not_exist(
    repository, visit: Visit, previously_deleted: bool
) -> None:
    """指定した user_id・visit_id の記録が未作成、または削除済みの場合を確認する。

    delete_visit が VisitNotFoundError を送出すること。
    その user_id で呼び出した list_visits の戻り値が空リストになること。
    """
    # Arrange
    if previously_deleted:
        repository.create_visit(visit)
        repository.delete_visit(visit.user_id, visit.visit_id)

    # Assert
    with pytest.raises(VisitNotFoundError):
        repository.delete_visit(visit.user_id, visit.visit_id)
    assert repository.list_visits(visit.user_id) == []


def test_delete_visit_failure_preserves_visit_when_another_user_is_specified(
    repository, visit: Visit, other_user_visit: Visit
) -> None:
    """ユーザーAだけが持つ記録を、ユーザーBの user_id で削除しようとする場合を確認する。

    delete_visit が VisitNotFoundError を送出すること。
    Aの一覧取得結果が、削除前と同じ記録を含むリストになること。
    """
    # Arrange
    repository.create_visit(visit)

    # Assert
    with pytest.raises(VisitNotFoundError):
        repository.delete_visit(other_user_visit.user_id, visit.visit_id)
    assert repository.list_visits(visit.user_id) == [visit]
