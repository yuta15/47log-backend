"""UserRepository 契約のテスト。"""

from src.modules.user_management.application import UserRepository


def test_user_repository_success_declares_expected_abstract_methods() -> None:
    """想定した抽象メソッドが定義されていることを確認する。"""
    assert UserRepository.__abstractmethods__ == {
        "create_user",
        "update_user",
        "get_user",
    }
