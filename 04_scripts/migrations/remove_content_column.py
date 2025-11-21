#!/usr/bin/env python3
"""
DBマイグレーション: discussionsとsolutionsテーブルからcontentカラムを削除

コンテンツはRedisに3日間キャッシュされるため、DBに保存する必要がなくなった。
"""

import sys
import sqlite3
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent.parent / "02_backend"
sys.path.insert(0, str(project_root))

from app.config import DATABASE_PATH


def migrate_discussions_table():
    """discussionsテーブルからcontentカラムを削除"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        print("📝 discussions テーブルのマイグレーション開始...")

        # 1. 新しいテーブルを作成（content カラムなし）
        cursor.execute("""
            CREATE TABLE discussions_new (
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
                author_tier TEXT,
                summary TEXT,
                tier_color TEXT,
                FOREIGN KEY (competition_id) REFERENCES competitions(id)
            )
        """)

        # 2. データを移行（content カラム以外）
        cursor.execute("""
            INSERT INTO discussions_new (
                id, competition_id, title, author, url, vote_count,
                comment_count, view_count, kaggle_created_at, category,
                is_pinned, created_at, updated_at, author_tier,
                summary, tier_color
            )
            SELECT
                id, competition_id, title, author, url, vote_count,
                comment_count, view_count, kaggle_created_at, category,
                is_pinned, created_at, updated_at, author_tier,
                summary, tier_color
            FROM discussions
        """)

        migrated_count = cursor.rowcount

        # 3. インデックスを再作成
        cursor.execute("""
            CREATE INDEX idx_discussions_competition_id
            ON discussions_new(competition_id)
        """)

        cursor.execute("""
            CREATE INDEX idx_discussions_vote_count
            ON discussions_new(vote_count DESC)
        """)

        cursor.execute("""
            CREATE INDEX idx_discussions_created_at
            ON discussions_new(kaggle_created_at DESC)
        """)

        # 4. 古いテーブルを削除
        cursor.execute("DROP TABLE discussions")

        # 5. 新しいテーブルをリネーム
        cursor.execute("ALTER TABLE discussions_new RENAME TO discussions")

        conn.commit()

        print(f"✅ discussions テーブル: {migrated_count}件のレコードを移行しました")
        return migrated_count

    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        raise
    finally:
        conn.close()


def migrate_solutions_table():
    """solutionsテーブルからcontentカラムを削除"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        print("📝 solutions テーブルのマイグレーション開始...")

        # 1. 新しいテーブルを作成（content カラムなし）
        cursor.execute("""
            CREATE TABLE solutions_new (
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
                summary TEXT,
                techniques TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (competition_id) REFERENCES competitions(id)
            )
        """)

        # 2. データを移行（content カラム以外）
        cursor.execute("""
            INSERT INTO solutions_new (
                id, competition_id, title, author, author_tier, tier_color,
                url, type, medal, rank, vote_count, comment_count,
                summary, techniques, created_at, updated_at
            )
            SELECT
                id, competition_id, title, author, author_tier, tier_color,
                url, type, medal, rank, vote_count, comment_count,
                summary, techniques, created_at, updated_at
            FROM solutions
        """)

        migrated_count = cursor.rowcount

        # 3. インデックスを再作成
        cursor.execute("""
            CREATE INDEX idx_solutions_competition_id
            ON solutions_new(competition_id)
        """)

        cursor.execute("""
            CREATE INDEX idx_solutions_type
            ON solutions_new(type)
        """)

        cursor.execute("""
            CREATE INDEX idx_solutions_rank
            ON solutions_new(rank ASC)
        """)

        cursor.execute("""
            CREATE INDEX idx_solutions_vote_count
            ON solutions_new(vote_count DESC)
        """)

        # 4. 古いテーブルを削除
        cursor.execute("DROP TABLE solutions")

        # 5. 新しいテーブルをリネーム
        cursor.execute("ALTER TABLE solutions_new RENAME TO solutions")

        conn.commit()

        print(f"✅ solutions テーブル: {migrated_count}件のレコードを移行しました")
        return migrated_count

    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        raise
    finally:
        conn.close()


def main():
    print("🗑️  contentカラムを削除するマイグレーションを実行します...\n")
    print("⚠️  注意: コンテンツはRedisに3日間キャッシュされます")
    print("⚠️  DBからcontentカラムを削除するとコンテンツは永久に失われます\n")

    # 確認
    response = input("続行しますか? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ マイグレーションをキャンセルしました")
        return

    try:
        disc_count = migrate_discussions_table()
        sol_count = migrate_solutions_table()

        total = disc_count + sol_count

        print(f"\n✨ マイグレーション完了: 合計 {total}件のレコードを移行しました")
        print("\n📝 変更内容:")
        print("   - discussions テーブルから content カラムを削除")
        print("   - solutions テーブルから content カラムを削除")
        print("   - コンテンツは Redis に3日間キャッシュされます")

    except Exception as e:
        print(f"\n❌ マイグレーション失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
