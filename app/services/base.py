from app.utils.db_manager import DB_Manager


class BaseService:
    db: DB_Manager | None

    def __init__(self, db: DB_Manager | None = None) -> None:
        self.db = db