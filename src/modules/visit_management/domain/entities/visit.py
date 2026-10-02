"""訪問記録のドメインエンティティ。"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .enums import Prefecture


@dataclass
class Visit:
    """都道府県への訪問記録を表す。"""

    user_id: UUID
    visit_id: UUID
    prefecture: Prefecture
    created_at: datetime
