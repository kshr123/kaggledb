#!/usr/bin/env python3
"""
DBマイグレーション: updated_at削除 & days_until_deadline追加

変更内容:
1. updated_at カラムを削除
2. created_at を日付のみに変更（YYYY-MM-DD）
3. days_until_deadline カラムを追加（開催中の場合のみ）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '02_backend'))

import sqlite3
from datetime import datetime, date
from app.config import DATABASE_PATH


def migrate():
    print("=" * 60)
    print("DBマイグレーション: updated_at削除 & days_until_deadline追加")
    print("=" * 60)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Step 1: 新しいテーブルを作成（updated_atなし、days_until_deadlineあり）
        print("\n[1/5] 新しいテーブル構造を作成中...")
        cursor.execute("""
            CREATE TABLE competitions_new (
                id                TEXT PRIMARY KEY,
                title             TEXT NOT NULL,
                url               TEXT NOT NULL,
                start_date        DATE,
                end_date          DATE,
                status            TEXT NOT NULL,
                metric            TEXT,
                description       TEXT,
                summary           TEXT,
                tags              TEXT,
                data_types        TEXT,
                domain            TEXT,
                discussion_count  INTEGER DEFAULT 0,
                solution_status   TEXT DEFAULT '未着手',
                created_at        DATE DEFAULT (date('now')),
                days_until_deadline INTEGER,
                last_scraped_at   TIMESTAMP,
                metric_description TEXT,
                dataset_info      TEXT,
                is_favorite       BOOLEAN DEFAULT 0
            )
        """)
        print("✅ 新しいテーブル作成完了")

        # Step 2: データをコピー（created_atを日付のみに変換）
        print("\n[2/5] データを新しいテーブルにコピー中...")
        cursor.execute("""
            INSERT INTO competitions_new (
                id, title, url, start_date, end_date, status, metric,
                description, summary, tags, data_types, domain,
                discussion_count, solution_status, created_at,
                last_scraped_at, metric_description, dataset_info, is_favorite
            )
            SELECT
                id, title, url, start_date, end_date, status, metric,
                description, summary, tags, data_types, domain,
                discussion_count, solution_status,
                date(created_at),  -- 日付のみに変換
                last_scraped_at, metric_description, dataset_info, is_favorite
            FROM competitions
        """)
        print(f"✅ {cursor.rowcount}件のデータをコピー完了")

        # Step 3: days_until_deadline を計算して更新（statusがactiveの場合のみ）
        print("\n[3/5] days_until_deadline を計算中...")
        cursor.execute("""
            SELECT id, end_date, status
            FROM competitions_new
            WHERE status = 'active' AND end_date IS NOT NULL
        """)
        active_comps = cursor.fetchall()

        today = date.today()
        updated_count = 0

        for comp_id, end_date_str, status in active_comps:
            try:
                # end_dateをパース
                end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                days_until = (end_date_obj - today).days

                if days_until >= 0:  # 未来の日付の場合のみ
                    cursor.execute("""
                        UPDATE competitions_new
                        SET days_until_deadline = ?
                        WHERE id = ?
                    """, (days_until, comp_id))
                    updated_count += 1
            except Exception as e:
                print(f"   ⚠️ {comp_id}: 日数計算エラー - {e}")

        print(f"✅ {updated_count}件のコンペに日数を設定")

        # Step 4: 古いテーブルを削除して新しいテーブルをリネーム
        print("\n[4/5] テーブルを入れ替え中...")
        cursor.execute("DROP TABLE competitions")
        cursor.execute("ALTER TABLE competitions_new RENAME TO competitions")
        print("✅ テーブル入れ替え完了")

        # Step 5: インデックスを再作成
        print("\n[5/5] インデックスを再作成中...")
        cursor.execute("CREATE INDEX idx_competitions_status ON competitions(status)")
        cursor.execute("CREATE INDEX idx_competitions_end_date ON competitions(end_date)")
        cursor.execute("CREATE INDEX idx_competitions_created_at ON competitions(created_at)")
        cursor.execute("CREATE INDEX idx_competitions_is_favorite ON competitions(is_favorite)")
        print("✅ インデックス作成完了")

        conn.commit()

        # 確認
        cursor.execute("SELECT COUNT(*) FROM competitions")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM competitions WHERE days_until_deadline IS NOT NULL")
        with_days = cursor.fetchone()[0]

        print("\n" + "=" * 60)
        print("マイグレーション完了！")
        print("=" * 60)
        print(f"総コンペ数: {total}件")
        print(f"終了日までの日数あり: {with_days}件")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        migrate()
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ マイグレーション失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
