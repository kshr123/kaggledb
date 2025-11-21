#!/usr/bin/env python3
"""
データベースに metric_description カラムを追加

評価指標の説明を保存するためのカラムを追加します。
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH


def add_metric_description_column():
    """metric_description カラムを追加"""

    print("=" * 60)
    print("データベーススキーマ更新: metric_description カラム追加")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # カラムが既に存在するか確認
    cursor.execute("PRAGMA table_info(competitions)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'metric_description' in columns:
        print("✅ metric_description カラムは既に存在します")
        conn.close()
        return

    try:
        # metric_description カラムを追加
        cursor.execute("""
            ALTER TABLE competitions
            ADD COLUMN metric_description TEXT
        """)

        conn.commit()
        print("✅ metric_description カラムを追加しました")

        # 確認
        cursor.execute("PRAGMA table_info(competitions)")
        columns = cursor.fetchall()

        print("\n📋 更新後のカラム一覧:")
        for col in columns:
            col_id, name, col_type, not_null, default, pk = col
            print(f"  - {name} ({col_type})")

    except Exception as e:
        print(f"❌ エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("マイグレーション完了")
    print("=" * 60)


if __name__ == "__main__":
    add_metric_description_column()
