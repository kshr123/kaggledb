#!/usr/bin/env python3
"""
Kaggleコンペ一覧スクレイピング + API詳細取得スクリプト

WebスクレイピングでコンペIDリストを取得し、
Kaggle APIで各コンペの詳細情報を取得してDBに保存
"""

import sys
import os
import argparse

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.services.scraper_service import get_scraper_service
from app.services.kaggle_client import get_kaggle_client
from app.config import DATABASE_PATH


def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='Webスクレイピング + Kaggle APIでコンペ情報を取得'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='スクレイピングする最大ページ数（デフォルト: 10）'
    )
    parser.add_argument(
        '--year-from',
        type=int,
        default=2020,
        help='取得する開始年（デフォルト: 2020）'
    )
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='キャッシュを無視して再取得'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細ログを表示'
    )

    return parser.parse_args()


def is_in_year_range(comp_data: dict, year_from: int) -> bool:
    """指定された年以降のコンペかどうかを判定"""
    try:
        date_str = comp_data.get('end_date') or comp_data.get('start_date')
        if not date_str:
            return False

        if isinstance(date_str, str):
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date = date_str

        return date.year >= year_from

    except Exception as e:
        print(f"   ⚠️ 日付パースエラー ({comp_data['id']}): {e}")
        return False


def main():
    args = parse_args()

    print("=" * 60)
    print("Kaggle コンペティション取得（スクレイピング + API）")
    print("=" * 60)
    print(f"最大ページ数: {args.max_pages}")
    print(f"開始年: {args.year_from}年以降")
    print("=" * 60)

    # Step 1: スクレイピングでコンペIDリストを取得
    print("\n[1/3] コンペIDリストをスクレイピング中...")
    scraper = get_scraper_service(cache_ttl_days=7)  # 1週間キャッシュ
    comp_ids = scraper.scrape_competitions_list(
        max_pages=args.max_pages,
        prestige_filter="medals",
        participation_filter="open",
        force_refresh=args.force_refresh
    )

    if not comp_ids:
        print("❌ コンペIDを取得できませんでした")
        return

    print(f"✅ {len(comp_ids)}件のコンペIDを取得")

    # Step 2: Kaggle APIで各コンペの詳細を取得
    print(f"\n[2/3] Kaggle APIで詳細情報を取得中...")
    kaggle_client = get_kaggle_client()

    if not kaggle_client.test_connection():
        print("❌ Kaggle API接続に失敗しました")
        return

    all_competitions = []
    for i, comp_id in enumerate(comp_ids, 1):
        try:
            comp_data = kaggle_client.get_competition_detail(comp_id)
            if comp_data:
                all_competitions.append(comp_data)
                if args.verbose:
                    print(f"   [{i}/{len(comp_ids)}] ✓ {comp_id}")
            else:
                if args.verbose:
                    print(f"   [{i}/{len(comp_ids)}] ✗ {comp_id} (取得失敗)")

        except Exception as e:
            if args.verbose:
                print(f"   [{i}/{len(comp_ids)}] ✗ {comp_id}: {e}")
            continue

    print(f"✅ {len(all_competitions)}件の詳細情報を取得")

    # Step 3: フィルタリングしてDBに保存
    print(f"\n[3/3] データベースに保存中...")
    print(f"   DB: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存データを確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    existing_count = cursor.fetchone()[0]
    print(f"   既存レコード: {existing_count}件")

    # フィルタリング
    filtered_competitions = []
    excluded_year = []

    for comp in all_competitions:
        if not is_in_year_range(comp, args.year_from):
            excluded_year.append(comp['title'])
            continue
        filtered_competitions.append(comp)

    print(f"   除外（{args.year_from}年以前）: {len(excluded_year)}件")
    print(f"   フィルタリング結果: {len(filtered_competitions)}件")

    # データを保存
    saved_count = 0
    updated_count = 0
    skipped_count = 0

    for comp in filtered_competitions:
        try:
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
                if args.verbose:
                    print(f"      📝 更新: {comp['title']}")
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
                    "[]",
                    "[]",
                    comp["domain"],
                    comp["discussion_count"],
                    comp["solution_status"],
                    comp["created_at"],
                    comp["updated_at"]
                ))
                saved_count += 1
                if args.verbose:
                    print(f"      ✅ 新規: {comp['title']}")

        except Exception as e:
            print(f"      ❌ エラー ({comp['id']}): {e}")
            skipped_count += 1
            continue

    conn.commit()

    # 最終確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    final_count = cursor.fetchone()[0]

    conn.close()

    # サマリー表示
    print("\n完了！")
    print("=" * 60)
    print(f"📊 結果サマリー:")
    print(f"   スクレイピング: {len(comp_ids)}件のコンペID")
    print(f"   API取得: {len(all_competitions)}件の詳細情報")
    print(f"   除外（{args.year_from}年以前）: {len(excluded_year)}件")
    print(f"   新規追加: {saved_count}件")
    print(f"   更新: {updated_count}件")
    print(f"   スキップ: {skipped_count}件")
    print(f"   データベース内総数: {final_count}件")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
