"""
データベース接続管理

SQLite接続のコンテキストマネージャーを提供します。
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from pathlib import Path


class Database:
    """データベース接続管理クラス"""

    def __init__(self, db_path: str | Path):
        """
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = str(db_path)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        データベース接続のコンテキストマネージャー

        Yields:
            sqlite3.Connection: データベース接続

        Example:
            >>> db = Database("data/kaggle.db")
            >>> with db.get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT * FROM competitions")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # カラム名でアクセス可能にする
        try:
            yield conn
        finally:
            conn.close()


def get_database() -> Database:
    """
    データベースインスタンスを取得（依存性注入用）

    Returns:
        Database: データベースインスタンス
    """
    from app.config import DATABASE_PATH
    return Database(DATABASE_PATH)
