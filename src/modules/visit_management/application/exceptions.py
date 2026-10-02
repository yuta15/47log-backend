"""訪問記録の永続化で発生する例外。"""


class VisitRepositoryError(Exception):
    """訪問記録の永続化処理で予期しないエラーが発生したことを表す。"""


class VisitAlreadyExistsError(VisitRepositoryError):
    """作成対象と同じ user_id・visit_id の訪問記録が既に存在することを表す。"""


class VisitNotFoundError(VisitRepositoryError):
    """指定した user_id・visit_id の訪問記録が存在しないことを表す。"""
