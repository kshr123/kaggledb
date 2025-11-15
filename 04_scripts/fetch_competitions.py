#!/usr/bin/env python3
"""
Kaggle コンペティションデータ取得スクリプト

Kaggle APIからコンペティション情報を取得してデータベースに保存
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.services.kaggle_client import get_kaggle_client
from app.config import DATABASE_PATH


def fetch_and_save_competitions(limit: int = 20):
    """
    Kaggle APIからコンペを取得してデータベースに保存

    Args:
        limit: 取得する最大件数（デフォルト20件）
    """
    print("=" * 60)
    print("Kaggle コンペティションデータ取得")
    print("=" * 60)

    # Kaggle APIクライアント初期化
    print("\n[1/4] Kaggle API接続中...")
    kaggle_client = get_kaggle_client()

    # 接続テスト
    if not kaggle_client.test_connection():
        print("❌ Kaggle API接続に失敗しました")
        print("   環境変数 KAGGLE_USERNAME と KAGGLE_KEY を確認してください")
        return

    print("✅ Kaggle API接続成功")

    # コンペティション一覧取得
    print(f"\n[2/4] コンペティション取得中（最大{limit}件）...")
    competitions = kaggle_client.get_competitions(page=1)

    if not competitions:
        print("❌ コンペティションの取得に失敗しました")
        return

    # 必要な件数だけ取得
    competitions = competitions[:limit]
    print(f"✅ {len(competitions)}件のコンペを取得しました")

    # データベース接続
    print(f"\n[3/4] データベースに保存中...")
    print(f"   DB: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存データを確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    existing_count = cursor.fetchone()[0]
    print(f"   既存レコード: {existing_count}件")

    # データを保存
    saved_count = 0
    updated_count = 0
    skipped_count = 0

    for comp in competitions:
        try:
            # 既存レコードを確認
            cursor.execute("SELECT id FROM competitions WHERE id = ?", (comp["id"],))
            existing = cursor.fetchone()

            if existing:
                # 更新
                cursor.execute("""
                    UPDATE competitions SET
                        title = ?,
                        url = ?,
                        start_date = ?,
                        end_date = ?,
                        status = ?,
                        metric = ?,
                        description = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    comp["title"],
                    comp["url"],
                    comp["start_date"],
                    comp["end_date"],
                    comp["status"],
                    comp["metric"],
                    comp["description"],
                    datetime.now().isoformat(),
                    comp["id"]
                ))
                updated_count += 1
                print(f"   📝 更新: {comp['title']}")
            else:
                # 新規挿入
                cursor.execute("""
                    INSERT INTO competitions (
                        id, title, url, start_date, end_date, status, metric,
                        description, summary, tags, data_types, domain,
                        discussion_count, solution_status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp["id"],
                    comp["title"],
                    comp["url"],
                    comp["start_date"],
                    comp["end_date"],
                    comp["status"],
                    comp["metric"],
                    comp["description"],
                    comp["summary"],
                    "[]",  # tags（JSON文字列）
                    "[]",  # data_types（JSON文字列）
                    comp["domain"],
                    comp["discussion_count"],
                    comp["solution_status"],
                    comp["created_at"],
                    comp["updated_at"]
                ))
                saved_count += 1
                print(f"   ✅ 新規: {comp['title']}")

        except Exception as e:
            print(f"   ❌ エラー ({comp['id']}): {e}")
            skipped_count += 1
            continue

    # コミット
    conn.commit()

    # 最終確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    final_count = cursor.fetchone()[0]

    conn.close()

    # サマリー表示
    print("\n[4/4] 完了！")
    print("=" * 60)
    print(f"📊 結果サマリー:")
    print(f"   新規追加: {saved_count}件")
    print(f"   更新: {updated_count}件")
    print(f"   スキップ: {skipped_count}件")
    print(f"   合計: {final_count}件（データベース内）")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kaggle コンペティションデータ取得")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="取得する最大件数（デフォルト: 20）"
    )

    args = parser.parse_args()

    try:
        fetch_and_save_competitions(limit=args.limit)
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
