#!/usr/bin/env python3
"""
説明文から評価指標を抽出してデータベースを更新
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime

from app.config import DATABASE_PATH
from app.services.llm_service import get_llm_service


def is_internal_code_name(metric: str) -> bool:
    """内部コード名かどうかを判定"""
    if not metric:
        return False
    has_underscore = '_' in metric
    has_space = ' ' in metric
    return has_underscore and not has_space


def get_competitions_to_update():
    """更新対象のコンペティションを取得"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # metricが空 or 内部コード名のコンペを取得
    cursor.execute("""
        SELECT id, title, description, metric
        FROM competitions
        WHERE description IS NOT NULL AND description != ''
    """)

    rows = cursor.fetchall()
    conn.close()

    competitions = []
    for row in rows:
        comp = dict(row)
        # metricが空、または内部コード名の場合のみ更新対象
        if not comp['metric'] or is_internal_code_name(comp['metric']):
            competitions.append(comp)

    return competitions


def update_metric(comp_id: str, metric: str) -> bool:
    """評価指標を更新"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE competitions SET metric = ?, updated_at = ? WHERE id = ?",
            (metric, datetime.now().isoformat(), comp_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 更新エラー ({comp_id}): {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="説明文から評価指標を抽出")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="処理する最大件数（省略時は全件）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には更新せず、処理内容のみ表示"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("評価指標抽出スクリプト（説明文から）")
    print("=" * 60)

    # LLMサービス初期化
    try:
        llm_service = get_llm_service()
        print("✅ LLMサービス初期化成功")
    except Exception as e:
        print(f"❌ LLMサービス初期化失敗: {e}")
        return

    # 更新対象のコンペティション取得
    competitions = get_competitions_to_update()
    if args.limit:
        competitions = competitions[:args.limit]

    if not competitions:
        print("✅ 更新が必要なコンペティションはありません")
        return

    print(f"📊 更新対象: {len(competitions)}件")
    print("-" * 60)

    # 各コンペティションを処理
    success_count = 0
    extracted_count = 0
    failed_count = 0

    for i, comp in enumerate(competitions, 1):
        print(f"\n[{i}/{len(competitions)}] {comp['title']}")
        print(f"  ID: {comp['id']}")
        print(f"  現在の指標: {comp['metric'] or '(空)'}")

        try:
            # 説明文から評価指標を抽出
            extracted_metric = llm_service.extract_evaluation_metric(
                description=comp['description'],
                title=comp['title']
            )

            if extracted_metric:
                print(f"  ✅ 抽出成功: {extracted_metric}")
                extracted_count += 1

                # データベース更新
                if not args.dry_run:
                    if update_metric(comp['id'], extracted_metric):
                        print(f"  💾 データベース更新成功")
                        success_count += 1
                    else:
                        print(f"  ❌ データベース更新失敗")
                        failed_count += 1
                else:
                    print(f"  🔍 [DRY RUN] データベース更新はスキップ")
                    success_count += 1
            else:
                print(f"  ⚠️  評価指標が見つかりませんでした")

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            failed_count += 1
            continue

    # サマリー
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)
    print(f"✅ 評価指標抽出成功: {extracted_count}件")
    print(f"✅ データベース更新成功: {success_count}件")
    if failed_count > 0:
        print(f"❌ 失敗: {failed_count}件")
    if args.dry_run:
        print("🔍 DRY RUN モード: 実際のデータベース更新は行われていません")


if __name__ == "__main__":
    main()
