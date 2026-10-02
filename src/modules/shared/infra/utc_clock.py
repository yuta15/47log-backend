"""UTC 時刻を返す Clock 実装。"""

from datetime import UTC, datetime

from ..domain import Clock


class UtcClock(Clock):
    """UTC の現在時刻を取得する。"""

    def now(self) -> datetime:
        """UTC の現在時刻を返す。"""
        return datetime.now(UTC)
