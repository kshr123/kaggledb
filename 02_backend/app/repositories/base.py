"""
BaseRepository - リポジトリ基底クラス
"""
from app.database import Database


class BaseRepository:
    """リポジトリ基底クラス"""

    def __init__(self, db: Database):
        """
        Args:
            db: データベースインスタンス
        """
        self.db = db
