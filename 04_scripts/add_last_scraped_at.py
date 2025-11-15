#!/usr/bin/env python3
"""
データベースマイグレーション: last_scraped_at カラムを追加

competitions テーブルに last_scraped_at カラムを追加する
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH


def add_last_scraped_at_column():
    """last_scraped_at カラムを追加"""
    print("=" * 60)
    print("データベースマイグレーション")
    print("=" * 60)
    print(f"データベース: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # カラムが既に存在するか確認
        cursor.execute("PRAGMA table_info(competitions)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'last_scraped_at' in columns:
            print("✅ last_scraped_at カラムは既に存在します")
            return

        # カラムを追加
        print("⚙️  last_scraped_at カラムを追加中...")
        cursor.execute("""
            ALTER TABLE competitions
            ADD COLUMN last_scraped_at TIMESTAMP
        """)

        conn.commit()
        print("✅ マイグレーション完了")

    except sqlite3.Error as e:
        print(f"❌ エラー: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    add_last_scraped_at_column()
