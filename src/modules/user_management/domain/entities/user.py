"""User domain entity."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .enums import UserStatus


# TODO: 今後dataclassを外す。現時点では
@dataclass
class User:
    """
    Represent a user.
    TODO: 現在Infra実装のための最小限の実装のため、今後以下を実施
        - ドメインルールを追加する。
        - dataclassを外しコンストラクタを実装する。
        - @property経由でgetする実装に修正し、propertyはprivate method実装にする。
    """

    user_id: UUID
    account_name: str
    created_at: datetime
    updated_at: datetime
    status: UserStatus
