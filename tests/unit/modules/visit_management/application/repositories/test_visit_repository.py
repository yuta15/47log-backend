"""VisitRepository 契約のテスト。"""

from src.modules.visit_management.application import VisitRepository


def test_visit_repository_success_declares_expected_abstract_methods() -> None:
    """想定した抽象メソッドが定義されていることを確認する。"""
    assert VisitRepository.__abstractmethods__ == {
        "create_visit",
        "delete_visit",
        "list_visits",
    }
