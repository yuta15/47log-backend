"""訪問記録の Repository 契約。"""

from abc import ABC, abstractmethod
from uuid import UUID

from ...domain import Visit


class VisitRepository(ABC):
    """訪問記録の取得・作成・削除の操作を定義する。"""

    @abstractmethod
    def list_visits(self, user_id: str) -> list[Visit]:
        """指定ユーザーの全訪問記録を visit_id の昇順で返す。

        訪問記録が存在しない場合は空リストを返す。
        """

    @abstractmethod
    def create_visit(self, visit: Visit) -> None:
        """訪問記録を作成する。同じ都道府県の複数登録を許可する。

        Raises:
            VisitAlreadyExistsError: 同じ user_id・visit_id の記録が存在する場合。
        """

    @abstractmethod
    def delete_visit(self, user_id: str, visit_id: UUID) -> None:
        """指定した user_id・visit_id の訪問記録を削除する。

        Raises:
            VisitNotFoundError: 指定した複合キーの記録が存在しない場合。
        """
