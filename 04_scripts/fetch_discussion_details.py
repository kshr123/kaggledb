#!/usr/bin/env python3
"""
ディスカッション詳細取得スクリプト

DBに保存されているディスカッションの詳細（content）を取得し、
要約（summary）を生成して保存します。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.config import DATABASE_PATH
from app.services.scraper_service import get_scraper_service
import time


def generate_summary(content: str) -> str:
    """
    コンテンツから要約を生成

    TODO: LLM APIを使用して要約を生成する
    現在は先頭500文字を返す簡易実装
    """
    # 簡易実装：先頭500文字を要約として使用
    if len(content) > 500:
        return content[:500] + "..."
    return content


def fetch_discussion_details(comp_id: str = None, limit: int = None, force_refresh: bool = False):
    """
    ディスカッション詳細を取得して保存

    Args:
        comp_id: コンペIDを指定すると、そのコンペのディスカッションのみ処理
        limit: 処理する最大件数
        force_refresh: 既にcontentがあるディスカッションも再取得
    """

    print(f"\n{'='*60}")
    print(f"ディスカッション詳細取得")
    print(f"{'='*60}\n")

    # DBから対象ディスカッションを取得
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # クエリ構築
    if force_refresh:
        if comp_id:
            query = "SELECT * FROM discussions WHERE competition_id = ?"
            params = (comp_id,)
        else:
            query = "SELECT * FROM discussions"
            params = ()
    else:
        if comp_id:
            query = "SELECT * FROM discussions WHERE competition_id = ? AND (content IS NULL OR content = '')"
            params = (comp_id,)
        else:
            query = "SELECT * FROM discussions WHERE content IS NULL OR content = ''"
            params = ()

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, params)
    discussions = cursor.fetchall()
    conn.close()

    if not discussions:
        print("✓ 処理対象のディスカッションがありません")
        return

    print(f"処理対象: {len(discussions)}件\n")

    scraper = get_scraper_service()

    success_count = 0
    failed_count = 0

    for idx, disc in enumerate(discussions, 1):
        print(f"[{idx}/{len(discussions)}] {disc['title']}")

        try:
            # ディスカッション詳細をスクレイピング
            detail = scraper.get_discussion_detail(
                discussion_url=disc['url'],
                force_refresh=force_refresh
            )

            if not detail or not detail.get('content'):
                print(f"  ❌ 取得失敗")
                failed_count += 1
                continue

            content = detail['content']

            # 要約を生成
            summary = generate_summary(content)

            # DBを更新
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE discussions
                SET content = ?,
                    summary = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                content,
                summary,
                datetime.now().isoformat(),
                disc['id']
            ))

            conn.commit()
            conn.close()

            print(f"  ✅ 保存完了 ({len(content)}文字)")
            success_count += 1

            # レート制限対策（最後の1件以外は待機）
            if idx < len(discussions):
                time.sleep(2)

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            failed_count += 1
            continue

    print(f"\n{'='*60}")
    print(f"処理完了:")
    print(f"  成功: {success_count}件")
    print(f"  失敗: {failed_count}件")
    print(f"{'='*60}\n")


def main():
    """メイン処理"""

    # テスト: titanicのディスカッション上位5件を取得
    fetch_discussion_details(
        comp_id='titanic',
        limit=5,
        force_refresh=False
    )


if __name__ == "__main__":
    main()
