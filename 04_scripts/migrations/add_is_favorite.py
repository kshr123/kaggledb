#!/usr/bin/env python3
"""
competitionsテーブルにis_favoriteカラムを追加するマイグレーション
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH


def migrate():
    """is_favoriteカラムを追加"""

    print("=" * 60)
    print("マイグレーション: is_favorite カラム追加")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # カラムを追加
        cursor.execute("""
            ALTER TABLE competitions
            ADD COLUMN is_favorite BOOLEAN DEFAULT 0
        """)

        print("✅ is_favorite カラムを追加しました")

        # インデックスを作成（お気に入りのみを効率的に取得するため）
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_competitions_is_favorite
            ON competitions(is_favorite)
        """)

        print("✅ インデックスを作成しました")

        conn.commit()

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️  is_favorite カラムは既に存在します")
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
