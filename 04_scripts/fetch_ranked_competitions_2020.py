#!/usr/bin/env python3
"""
2020年以降のランク付きコンペティション取得スクリプト

Kaggle APIから2020年以降のランク付きコンペのみを取得してデータベースに保存
練習コンペ（playground/getting-started）は除外し、既存の練習コンペはDBから削除
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.services.kaggle_client import get_kaggle_client
from app.config import DATABASE_PATH


def is_ranked_competition(comp_data: dict) -> bool:
    """
    ランク付きコンペかどうかを判定（練習コンペを除外）

    Args:
        comp_data: コンペティション情報

    Returns:
        bool: ランク付きコンペの場合True
    """
    title_lower = comp_data['title'].lower()
    id_lower = comp_data['id'].lower()

    # 除外キーワード（練習・チュートリアル系）
    exclude_keywords = [
        'playground', 'getting started', 'getting-started',
        'tutorial', 'beginner', 'practice', 'learning',
        'intro to', 'introduction to', 'learn'
    ]

    for keyword in exclude_keywords:
        if keyword in title_lower or keyword in id_lower:
            return False

    return True


def is_after_2020(comp_data: dict) -> bool:
    """
    2020年以降のコンペかどうかを判定

    Args:
        comp_data: コンペティション情報

    Returns:
        bool: 2020年以降の場合True
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

        return date.year >= 2020
    except Exception as e:
        print(f"   ⚠️  日付パースエラー ({comp_data['id']}): {e}")
        return False


def delete_practice_competitions(conn):
    """
    既存の練習コンペをDBから削除

    Args:
        conn: データベース接続

    Returns:
        int: 削除件数
    """
    cursor = conn.cursor()

    # 練習コンペを検索
    exclude_keywords = [
        '%playground%', '%getting started%', '%tutorial%',
        '%beginner%', '%practice%', '%learning%', '%intro to%'
    ]

    where_clauses = []
    for keyword in exclude_keywords:
        where_clauses.append(f"LOWER(title) LIKE '{keyword}'")
        where_clauses.append(f"LOWER(id) LIKE '{keyword}'")

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


def fetch_and_save_ranked_competitions():
    """
    2020年以降のランク付きコンペを取得してデータベースに保存
    """
    print("=" * 60)
    print("2020年以降のランク付きコンペティション取得")
    print("=" * 60)

    # Kaggle APIクライアント初期化
    print("\n[1/5] Kaggle API接続中...")
    kaggle_client = get_kaggle_client()

    # 接続テスト
    if not kaggle_client.test_connection():
        print("❌ Kaggle API接続に失敗しました")
        print("   環境変数 KAGGLE_USERNAME と KAGGLE_KEY を確認してください")
        return

    print("✅ Kaggle API接続成功")

    # コンペティション一覧取得（全カテゴリ・複数ページ）
    print(f"\n[2/5] コンペティション取得中...")
    all_competitions = []
    max_pages = 100  # 2020年以降の全コンペを取得するため多めに

    print(f"   全カテゴリから取得中...")
    for page in range(1, max_pages + 1):
        try:
            comps = kaggle_client.get_competitions(page=page)
            if not comps:
                print(f"   ページ {page} でデータなし、取得終了")
                break
            all_competitions.extend(comps)
            if page % 10 == 0:
                print(f"   ページ {page}: 累計 {len(all_competitions)}件取得")
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

    # フィルタリング: 2020年以降 & ランク付き
    print(f"\n[3/5] フィルタリング中（2020年以降 & ランク付き）...")
    filtered_competitions = []
    excluded_practice = []

    for comp in unique_competitions:
        # 2020年以降チェック
        if not is_after_2020(comp):
            continue

        # ランク付きコンペチェック（練習コンペを除外）
        if not is_ranked_competition(comp):
            excluded_practice.append(comp['title'])
            continue

        filtered_competitions.append(comp)

    print(f"   除外された練習コンペ: {len(excluded_practice)}件")
    if excluded_practice[:5]:  # 最初の5件を表示
        for title in excluded_practice[:5]:
            print(f"      - {title}")
        if len(excluded_practice) > 5:
            print(f"      ... 他 {len(excluded_practice) - 5}件")

    print(f"✅ {len(filtered_competitions)}件のランク付きコンペ（2020年以降）")

    # データベース接続
    print(f"\n[4/5] データベース操作中...")
    print(f"   DB: {DATABASE_PATH}")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存データを確認
    cursor.execute("SELECT COUNT(*) FROM competitions")
    existing_count = cursor.fetchone()[0]
    print(f"   既存レコード: {existing_count}件")

    # 練習コンペを削除
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
    print(f"   除外（2020年以前）: {len(unique_competitions) - len(filtered_competitions) - len(excluded_practice)}件")
    print(f"   除外（練習コンペ）: {len(excluded_practice)}件")
    print(f"   2020年以降 & ランク付き: {len(filtered_competitions)}件")
    print(f"   DB削除（練習コンペ）: {deleted_count}件")
    print(f"   新規追加: {saved_count}件")
    print(f"   更新: {updated_count}件")
    print(f"   スキップ: {skipped_count}件")
    print(f"   データベース内総数: {final_count}件")
    print("=" * 60)


if __name__ == "__main__":
    try:
        fetch_and_save_ranked_competitions()
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
