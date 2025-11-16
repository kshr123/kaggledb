#!/usr/bin/env python3
"""
ソリューションテーブル追加マイグレーション

solutions テーブルを作成します。
コンペティションの上位解法やSolutionタグのディスカッションを保存します。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '02_backend'))

import sqlite3
from app.config import DATABASE_PATH


def migrate():
    """ソリューションテーブルを追加"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存のテーブルを削除（開発中のため）
    cursor.execute("DROP TABLE IF EXISTS solutions")

    # solutions テーブル作成
    cursor.execute("""
        CREATE TABLE solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id TEXT NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            author_tier TEXT,
            tier_color TEXT,
            url TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('notebook', 'discussion')),
            medal TEXT CHECK(medal IN ('gold', 'silver', 'bronze')),
            rank INTEGER,
            vote_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            content TEXT,
            summary TEXT,
            techniques TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (competition_id) REFERENCES competitions(id)
        )
    """)

    # インデックス作成
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_solutions_competition_id
        ON solutions(competition_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_solutions_type
        ON solutions(type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_solutions_rank
        ON solutions(rank ASC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_solutions_vote_count
        ON solutions(vote_count DESC)
    """)

    conn.commit()
    conn.close()

    print("✅ solutions テーブルを作成しました")
    print("  - id: 主キー")
    print("  - competition_id: コンペティションID（外部キー）")
    print("  - title: ソリューションタイトル")
    print("  - author: 投稿者名")
    print("  - author_tier: Kaggle称号（Grandmaster, Master等）")
    print("  - tier_color: 称号色（RGB）")
    print("  - url: Kaggleのノートブック/ディスカッションURL")
    print("  - type: 種類（notebook/discussion）")
    print("  - medal: メダル（gold/silver/bronze）")
    print("  - rank: 順位（1位、2位等）")
    print("  - vote_count: 投票数")
    print("  - comment_count: コメント数")
    print("  - content: 全文")
    print("  - summary: LLM要約")
    print("  - techniques: 使用技術（LLM抽出）")
    print("  - created_at: データベース登録日時")
    print("  - updated_at: データベース更新日時")


if __name__ == "__main__":
    migrate()
