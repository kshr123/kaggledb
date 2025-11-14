"""
データベース初期化スクリプト

Usage:
    python -m app.batch.init_db
    python -m app.batch.init_db --reset  # 既存DBを削除して再作成
"""

import sqlite3
import sys
from pathlib import Path
from typing import Optional


def get_schema_path() -> Path:
    """schema.sqlのパスを取得"""
    # backend/schema.sql
    return Path(__file__).parent.parent.parent / "schema.sql"


def initialize_database(db_path: str) -> None:
    """
    データベースを初期化する

    Args:
        db_path: データベースファイルのパス
    """
    schema_path = get_schema_path()

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    # schema.sqlを読み込み
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # データベース接続
    conn = sqlite3.connect(db_path)

    try:
        # 外部キー制約を有効化
        conn.execute("PRAGMA foreign_keys = ON")

        # スキーマを実行
        conn.executescript(schema_sql)
        conn.commit()

        print(f"✅ Database initialized successfully: {db_path}")

        # 統計情報を表示
        cursor = conn.cursor()

        # テーブル数
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        table_count = cursor.fetchone()[0]

        # タグ数
        cursor.execute("SELECT COUNT(*) FROM tags")
        tag_count = cursor.fetchone()[0]

        # インデックス数
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        index_count = cursor.fetchone()[0]

        print(f"   - Tables created: {table_count}")
        print(f"   - Initial tags: {tag_count}")
        print(f"   - Indexes created: {index_count}")

    except sqlite3.Error as e:
        print(f"❌ Error initializing database: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()


def main():
    """メイン処理"""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Initialize Kaggle Knowledge Base database"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing database and create new one"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Database file path (default: from DATABASE_PATH env var or ./data/kaggle_competitions.db)"
    )

    args = parser.parse_args()

    # データベースパスの決定
    if args.db_path:
        db_path = args.db_path
    else:
        # 環境変数から取得、なければデフォルト
        db_path = os.getenv("DATABASE_PATH", "./data/kaggle_competitions.db")

    # dataディレクトリが存在しない場合は作成
    db_dir = Path(db_path).parent
    if not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {db_dir}")

    # --reset オプションが指定された場合、既存DBを削除
    if args.reset:
        if Path(db_path).exists():
            Path(db_path).unlink()
            print(f"🗑️  Deleted existing database: {db_path}")

    # データベース初期化
    try:
        initialize_database(db_path)
    except Exception as e:
        print(f"Failed to initialize database: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
