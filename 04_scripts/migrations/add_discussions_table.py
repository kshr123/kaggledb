#!/usr/bin/env python3
"""
ディスカッションテーブル追加マイグレーション

discussions テーブルを作成します。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH


def migrate():
    """ディスカッションテーブルを追加"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存のテーブルを削除（開発中のため）
    cursor.execute("DROP TABLE IF EXISTS discussions")

    # discussions テーブル作成
    cursor.execute("""
        CREATE TABLE discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            url TEXT NOT NULL,
            vote_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            kaggle_created_at TEXT,
            category TEXT,
            is_pinned BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (competition_id) REFERENCES competitions(id)
        )
    """)

    # インデックス作成
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_discussions_competition_id
        ON discussions(competition_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_discussions_vote_count
        ON discussions(vote_count DESC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_discussions_created_at
        ON discussions(kaggle_created_at DESC)
    """)

    conn.commit()
    conn.close()

    print("✅ discussions テーブルを作成しました")
    print("  - id: 主キー")
    print("  - competition_id: コンペティションID（外部キー）")
    print("  - title: ディスカッションタイトル")
    print("  - author: 投稿者名")
    print("  - url: KaggleのディスカッションURL")
    print("  - vote_count: 投票数")
    print("  - comment_count: コメント数")
    print("  - view_count: 閲覧数")
    print("  - kaggle_created_at: Kaggle上の投稿日時")
    print("  - category: カテゴリ（General, Questions, など）")
    print("  - is_pinned: ピン留めされているか")
    print("  - created_at: データベース登録日時")
    print("  - updated_at: データベース更新日時")


if __name__ == "__main__":
    migrate()
