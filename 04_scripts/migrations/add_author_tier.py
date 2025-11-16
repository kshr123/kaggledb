#!/usr/bin/env python3
"""
discussionsテーブルにauthor_tierカラムを追加するマイグレーション
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH


def migrate():
    """author_tierカラムを追加"""

    print("=" * 60)
    print("マイグレーション: author_tier カラム追加")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # カラムを追加（既に存在する場合はエラーになるが、それで問題ない）
        cursor.execute("""
            ALTER TABLE discussions
            ADD COLUMN author_tier TEXT
        """)

        print("✅ author_tier カラムを追加しました")

        conn.commit()

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️  author_tier カラムは既に存在します")
        else:
            raise

    finally:
        conn.close()

    print("=" * 60)
    print("マイグレーション完了")
    print("=" * 60)


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
