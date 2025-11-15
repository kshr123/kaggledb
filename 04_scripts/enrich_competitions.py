#!/usr/bin/env python3
"""
コンペティション情報充実化スクリプト

既存のコンペティションデータに対して、LLMを使用して以下を生成・更新します：
- 日本語要約 (summary)
- データタイプ (data_types)
- タグ (tags)
- ドメイン (domain)
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
import json
from datetime import datetime
from typing import List, Dict

from app.config import DATABASE_PATH
from app.services.llm_service import get_llm_service


def get_available_tags() -> Dict[str, List[str]]:
    """
    データベースからタグマスタを取得

    Returns:
        カテゴリ別のタグリスト
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, category FROM tags ORDER BY category, display_order")
    rows = cursor.fetchall()

    tags_by_category = {}
    for name, category in rows:
        if category not in tags_by_category:
            tags_by_category[category] = []
        tags_by_category[category].append(name)

    conn.close()
    return tags_by_category


def get_competitions_to_enrich(limit: int = None) -> List[Dict]:
    """
    充実化が必要なコンペティションを取得

    Args:
        limit: 取得する最大件数（Noneの場合は全件）

    Returns:
        コンペティション情報のリスト
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # summary または tags が空のコンペティションを取得
    query = """
        SELECT
            id, title, url, start_date, end_date, status,
            metric, description, summary, tags, data_types, domain
        FROM competitions
        WHERE (summary IS NULL OR summary = '' OR tags IS NULL OR tags = '[]' OR tags = '')
        AND description IS NOT NULL
        AND description != ''
        ORDER BY created_at DESC
    """

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    rows = cursor.fetchall()

    competitions = []
    for row in rows:
        comp = dict(row)
        # JSON文字列をPythonオブジェクトに変換
        if comp.get("tags"):
            try:
                comp["tags"] = json.loads(comp["tags"])
            except:
                comp["tags"] = []
        else:
            comp["tags"] = []

        if comp.get("data_types"):
            try:
                comp["data_types"] = json.loads(comp["data_types"])
            except:
                comp["data_types"] = []
        else:
            comp["data_types"] = []

        competitions.append(comp)

    conn.close()
    return competitions


def update_competition(competition: Dict) -> bool:
    """
    コンペティション情報をデータベースに更新

    Args:
        competition: 更新するコンペティション情報

    Returns:
        成功したかどうか
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # JSON配列を文字列に変換
        tags_json = json.dumps(competition.get("tags", []), ensure_ascii=False)
        data_types_json = json.dumps(competition.get("data_types", []), ensure_ascii=False)

        cursor.execute("""
            UPDATE competitions
            SET
                summary = ?,
                tags = ?,
                data_types = ?,
                domain = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            competition.get("summary", ""),
            tags_json,
            data_types_json,
            competition.get("domain", ""),
            datetime.now().isoformat(),
            competition["id"]
        ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ 更新エラー: {e}")
        conn.close()
        return False


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description="コンペティション情報をLLMで充実化")
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
    print("コンペティション情報充実化スクリプト")
    print("=" * 60)

    # LLMサービス初期化
    try:
        llm_service = get_llm_service()
        print("✅ LLMサービス初期化成功")
    except Exception as e:
        print(f"❌ LLMサービス初期化失敗: {e}")
        print("💡 OPENAI_API_KEY が .env に設定されているか確認してください")
        return

    # タグマスタ取得
    available_tags = get_available_tags()
    print(f"✅ タグマスタ取得: {sum(len(tags) for tags in available_tags.values())}件")

    # 充実化対象のコンペティション取得
    competitions = get_competitions_to_enrich(limit=args.limit)
    if not competitions:
        print("✅ 充実化が必要なコンペティションはありません")
        return

    print(f"📊 充実化対象: {len(competitions)}件")
    print("-" * 60)

    # 各コンペティションを処理
    success_count = 0
    error_count = 0

    for i, comp in enumerate(competitions, 1):
        print(f"\n[{i}/{len(competitions)}] {comp['title']}")
        print(f"  ID: {comp['id']}")

        try:
            # LLMで充実化
            enriched = llm_service.enrich_competition(comp, available_tags)

            # 結果を表示
            if enriched.get("summary"):
                print(f"  ✅ 要約生成: {len(enriched['summary'])}文字")
            if enriched.get("data_types"):
                print(f"  ✅ データタイプ: {', '.join(enriched['data_types'])}")
            if enriched.get("tags"):
                print(f"  ✅ タグ: {', '.join(enriched['tags'][:5])}" +
                      (f" (+{len(enriched['tags'])-5}個)" if len(enriched['tags']) > 5 else ""))
            if enriched.get("domain"):
                print(f"  ✅ ドメイン: {enriched['domain']}")

            # データベース更新
            if not args.dry_run:
                if update_competition(enriched):
                    print(f"  💾 データベース更新成功")
                    success_count += 1
                else:
                    print(f"  ❌ データベース更新失敗")
                    error_count += 1
            else:
                print(f"  🔍 [DRY RUN] データベース更新はスキップ")
                success_count += 1

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            error_count += 1
            continue

    # サマリー
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)
    print(f"✅ 成功: {success_count}件")
    if error_count > 0:
        print(f"❌ 失敗: {error_count}件")
    if args.dry_run:
        print("🔍 DRY RUN モード: 実際のデータベース更新は行われていません")


if __name__ == "__main__":
    main()
