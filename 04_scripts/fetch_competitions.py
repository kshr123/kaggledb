#!/usr/bin/env python3
"""
Kaggle コンペティション取得スクリプト（汎用版）

Kaggle APIからコンペを取得してデータベースに保存
フィルター条件（年、カテゴリー、練習コンペ除外）をコマンドライン引数で指定可能
"""

import sys
import os
import argparse
from typing import List, Optional, Dict, Any

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.services.kaggle_client import get_kaggle_client
from app.config import DATABASE_PATH


# デフォルトの練習コンペ除外キーワード
DEFAULT_PRACTICE_KEYWORDS = [
    'playground', 'getting started', 'getting-started',
    'tutorial', 'beginner', 'practice', 'learning',
    'intro to', 'introduction to', 'learn'
]


def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description='Kaggle APIからコンペティション情報を取得してDBに保存',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 2020年以降のランク付きコンペを取得（デフォルト）
  python fetch_competitions.py

  # 2022年以降のfeaturedコンペのみを取得
  python fetch_competitions.py --year-from 2022 --category featured

  # 全コンペを取得（練習コンペ含む）
  python fetch_competitions.py --year-from 2000 --include-practice

  # 特定のキーワードで検索
  python fetch_competitions.py --search "nlp"
        """
    )

    # フィルター条件
    parser.add_argument(
        '--year-from',
        type=int,
        default=2020,
        help='取得する開始年（デフォルト: 2020）'
    )
    parser.add_argument(
        '--year-to',
        type=int,
        default=None,
        help='取得する終了年（デフォルト: なし=現在まで）'
    )
    parser.add_argument(
        '--category',
        type=str,
        choices=['featured', 'research', 'playground', 'gettingStarted', 'all'],
        default='all',
        help='カテゴリーフィルター（デフォルト: all）'
    )
    parser.add_argument(
        '--search',
        type=str,
        default='',
        help='検索キーワード'
    )

    # 練習コンペ除外
    parser.add_argument(
        '--include-practice',
        action='store_true',
        help='練習コンペも含める（デフォルトは除外）'
    )
    parser.add_argument(
        '--delete-practice',
        action='store_true',
        default=True,
        help='DBから既存の練習コンペを削除する（デフォルト: True）'
    )
    parser.add_argument(
        '--no-delete-practice',
        dest='delete_practice',
        action='store_false',
        help='DBから練習コンペを削除しない'
    )

    # 取得オプション
    parser.add_argument(
        '--max-pages',
        type=int,
        default=100,
        help='最大取得ページ数（デフォルト: 100）'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='最大取得件数（デフォルト: なし）'
    )

    # 出力オプション
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細ログを表示'
    )

    return parser.parse_args()


def is_in_year_range(
    comp_data: Dict[str, Any],
    year_from: int,
    year_to: Optional[int] = None
) -> bool:
    """
    指定された年の範囲内のコンペかどうかを判定

    Args:
        comp_data: コンペティション情報
        year_from: 開始年
        year_to: 終了年（Noneの場合は制限なし）

    Returns:
        bool: 範囲内の場合True
    """
    try:
        # start_date または end_date で判定
        date_str = comp_data.get('end_date') or comp_data.get('start_date')

        if not date_str:
            return False

        # ISO形式の日付をパース
        if isinstance(date_str, str):
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date = date_str

        year = date.year

        # 範囲チェック
        if year < year_from:
            return False
        if year_to and year > year_to:
            return False

        return True

    except Exception as e:
        print(f"   ⚠️  日付パースエラー ({comp_data['id']}): {e}")
        return False


def is_practice_competition(
    comp_data: Dict[str, Any],
    keywords: List[str] = None
) -> bool:
    """
    練習コンペかどうかを判定

    Args:
        comp_data: コンペティション情報
        keywords: 除外キーワードリスト（Noneの場合はデフォルト）

    Returns:
        bool: 練習コンペの場合True
    """
    if keywords is None:
        keywords = DEFAULT_PRACTICE_KEYWORDS

    title_lower = comp_data['title'].lower()
    id_lower = comp_data['id'].lower()

    for keyword in keywords:
        if keyword in title_lower or keyword in id_lower:
            return True

    return False


def delete_practice_competitions(
    conn: sqlite3.Connection,
    keywords: List[str] = None
) -> int:
    """
    既存の練習コンペをDBから削除

    Args:
        conn: データベース接続
        keywords: 除外キーワードリスト（Noneの場合はデフォルト）

    Returns:
        int: 削除件数
    """
    if keywords is None:
        keywords = DEFAULT_PRACTICE_KEYWORDS

    cursor = conn.cursor()

    # 練習コンペを検索
    where_clauses = []
    for keyword in keywords:
        where_clauses.append(f"LOWER(title) LIKE '%{keyword}%'")
        where_clauses.append(f"LOWER(id) LIKE '%{keyword}%'")

    query = f"SELECT id, title FROM competitions WHERE {' OR '.join(where_clauses)}"
    cursor.execute(query)
    practice_comps = cursor.fetchall()

    if not practice_comps:
        print("   削除対象の練習コンペはありません")
        return 0

    print(f"\n   🗑️  {len(practice_comps)}件の練習コンペを削除:")
    for comp_id, title in practice_comps:
        print(f"      - {title} ({comp_id})")
        cursor.execute("DELETE FROM competitions WHERE id = ?", (comp_id,))

    conn.commit()
    return len(practice_comps)


def fetch_and_save_competitions(
    year_from: int = 2020,
    year_to: Optional[int] = None,
    category: str = 'all',
    search: str = '',
    include_practice: bool = False,
    delete_practice: bool = True,
    max_pages: int = 100,
    limit: Optional[int] = None,
    verbose: bool = False
) -> Dict[str, int]:
    """
    Kaggle APIからコンペを取得してデータベースに保存

    Args:
        year_from: 開始年
        year_to: 終了年（Noneの場合は制限なし）
        category: カテゴリーフィルター（'all'の場合は全カテゴリー）
        search: 検索キーワード
        include_practice: 練習コンペを含めるか
        delete_practice: DBから練習コンペを削除するか
        max_pages: 最大取得ページ数
        limit: 最大取得件数
        verbose: 詳細ログを表示するか

    Returns:
        dict: 結果サマリー
    """
    print("=" * 60)
    print("Kaggle コンペティション取得")
    print("=" * 60)
    print(f"フィルター条件:")
    print(f"  期間: {year_from}年以降" + (f"～{year_to}年" if year_to else "～現在"))
    print(f"  カテゴリー: {category}")
    if search:
        print(f"  検索: {search}")
    print(f"  練習コンペ: {'含む' if include_practice else '除外'}")
    print("=" * 60)

    # Kaggle APIクライアント初期化
    print("\n[1/5] Kaggle API接続中...")
    kaggle_client = get_kaggle_client()

    # 接続テスト
    if not kaggle_client.test_connection():
        print("❌ Kaggle API接続に失敗しました")
        print("   環境変数 KAGGLE_USERNAME と KAGGLE_KEY を確認してください")
        return {}

    print("✅ Kaggle API接続成功")

    # コンペティション一覧取得
    print(f"\n[2/5] コンペティション取得中...")
    all_competitions = []

    # カテゴリーフィルター
    category_param = None if category == 'all' else category

    if category_param:
        print(f"   カテゴリー: {category}")
    else:
        print(f"   全カテゴリから取得中...")

    for page in range(1, max_pages + 1):
        try:
            comps = kaggle_client.get_competitions(
                page=page,
                search=search,
                category=category_param
            )
            if not comps:
                print(f"   ページ {page} でデータなし、取得終了")
                break

            all_competitions.extend(comps)

            if verbose or page % 10 == 0:
                print(f"   ページ {page}: 累計 {len(all_competitions)}件取得")

            # limit指定がある場合はチェック
            if limit and len(all_competitions) >= limit:
                print(f"   上限 {limit}件に到達、取得終了")
                all_competitions = all_competitions[:limit]
                break

        except Exception as e:
            print(f"   ⚠️  ページ {page} の取得に失敗: {e}")
            break

    # 重複削除
    seen_ids = set()
    unique_competitions = []
    for comp in all_competitions:
        if comp['id'] not in seen_ids:
            seen_ids.add(comp['id'])
            unique_competitions.append(comp)

    print(f"✅ 合計 {len(unique_competitions)}件のユニークなコンペを取得しました")

    # フィルタリング
    print(f"\n[3/5] フィルタリング中...")
    filtered_competitions = []
    excluded_year = []
    excluded_practice = []

    for comp in unique_competitions:
        # 年チェック
        if not is_in_year_range(comp, year_from, year_to):
            excluded_year.append(comp['title'])
            continue

        # 練習コンペチェック
        if not include_practice and is_practice_competition(comp):
            excluded_practice.append(comp['title'])
            continue

        filtered_competitions.append(comp)

    print(f"   除外（期間外）: {len(excluded_year)}件")
    if not include_practice:
        print(f"   除外（練習コンペ）: {len(excluded_practice)}件")
        if verbose and excluded_practice[:5]:
            for title in excluded_practice[:5]:
                print(f"      - {title}")
            if len(excluded_practice) > 5:
                print(f"      ... 他 {len(excluded_practice) - 5}件")

    print(f"✅ {len(filtered_competitions)}件のコンペをフィルタリング完了")

    # データベース接続
    print(f"\n[4/5] データベース操作中...")
    print(f"   DB: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存データを確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    existing_count = cursor.fetchone()[0]
    print(f"   既存レコード: {existing_count}件")

    # 練習コンペを削除（オプション）
    deleted_count = 0
    if delete_practice and not include_practice:
        deleted_count = delete_practice_competitions(conn)

    # データを保存
    print(f"\n   💾 データ保存中...")
    saved_count = 0
    updated_count = 0
    skipped_count = 0

    for comp in filtered_competitions:
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
                if verbose:
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
                    "[]",  # tags（JSON文字列）
                    "[]",  # data_types（JSON文字列）
                    comp["domain"],
                    comp["discussion_count"],
                    comp["solution_status"],
                    comp["created_at"],
                    comp["updated_at"]
                ))
                saved_count += 1
                if verbose:
                    print(f"      ✅ 新規: {comp['title']}")

        except Exception as e:
            print(f"      ❌ エラー ({comp['id']}): {e}")
            skipped_count += 1
            continue

    # コミット
    conn.commit()

    # 最終確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    final_count = cursor.fetchone()[0]

    conn.close()

    # サマリー表示
    print("\n[5/5] 完了！")
    print("=" * 60)
    print(f"📊 結果サマリー:")
    print(f"   Kaggle API取得総数: {len(all_competitions)}件")
    print(f"   ユニーク: {len(unique_competitions)}件")
    print(f"   除外（期間外）: {len(excluded_year)}件")
    if not include_practice:
        print(f"   除外（練習コンペ）: {len(excluded_practice)}件")
    print(f"   フィルタリング結果: {len(filtered_competitions)}件")
    if delete_practice:
        print(f"   DB削除（練習コンペ）: {deleted_count}件")
    print(f"   新規追加: {saved_count}件")
    print(f"   更新: {updated_count}件")
    print(f"   スキップ: {skipped_count}件")
    print(f"   データベース内総数: {final_count}件")
    print("=" * 60)

    return {
        'fetched': len(all_competitions),
        'unique': len(unique_competitions),
        'excluded_year': len(excluded_year),
        'excluded_practice': len(excluded_practice),
        'filtered': len(filtered_competitions),
        'deleted': deleted_count,
        'saved': saved_count,
        'updated': updated_count,
        'skipped': skipped_count,
        'total': final_count
    }


if __name__ == "__main__":
    try:
        args = parse_args()

        result = fetch_and_save_competitions(
            year_from=args.year_from,
            year_to=args.year_to,
            category=args.category,
            search=args.search,
            include_practice=args.include_practice,
            delete_practice=args.delete_practice,
            max_pages=args.max_pages,
            limit=args.limit,
            verbose=args.verbose
        )

    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
