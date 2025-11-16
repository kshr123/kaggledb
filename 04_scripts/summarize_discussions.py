#!/usr/bin/env python3
"""
ディスカッション詳細取得＋要約スクリプト

指定したコンペティションのディスカッション詳細を取得し、
LLMで要約してデータベースに保存します。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.config import DATABASE_PATH
from app.services.scraper_service import get_scraper_service
from app.services.llm_service import get_llm_service


def summarize_discussion_for_competition(comp_id: str, max_discussions: int = 10):
    """
    コンペティションのディスカッションを取得・要約してDBに保存
    
    Args:
        comp_id: コンペティションID
        max_discussions: 要約する最大ディスカッション数
    """
    print(f"\n{'='*60}")
    print(f"ディスカッション要約: {comp_id}")
    print(f"{'='*60}\n")

    # サービス取得
    scraper = get_scraper_service()
    llm = get_llm_service()

    # データベースからディスカッション一覧を取得
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 要約がまだないディスカッションを取得（投票数順）
    cursor.execute("""
        SELECT id, title, url, vote_count
        FROM discussions
        WHERE competition_id = ?
          AND (summary IS NULL OR summary = '')
          AND is_pinned = 0
        ORDER BY vote_count DESC
        LIMIT ?
    """, (comp_id, max_discussions))

    discussions = cursor.fetchall()

    if not discussions:
        print(f"✓ 要約対象のディスカッションがありません")
        conn.close()
        return

    print(f"📋 {len(discussions)}件のディスカッションを要約します\n")

    # 各ディスカッションを処理
    summarized_count = 0
    skipped_count = 0

    for idx, disc in enumerate(discussions, 1):
        disc_id = disc['id']
        title = disc['title']
        url = disc['url']
        vote_count = disc['vote_count']

        print(f"[{idx}/{len(discussions)}] {title[:60]}... (👍 {vote_count})")

        # ディスカッション詳細を取得
        detail = scraper.get_discussion_detail(url, force_refresh=False)

        if not detail or not detail.get('content'):
            print(f"  ⚠️  内容取得失敗 - スキップ")
            skipped_count += 1
            continue

        content = detail['content']
        print(f"  ✓ 内容取得完了 ({len(content)}文字)")

        # LLMで要約
        print(f"  🤖 LLM要約中...")
        summary = llm.summarize_discussion(content=content, title=title)

        if not summary:
            print(f"  ⚠️  要約生成失敗 - スキップ")
            skipped_count += 1
            continue

        print(f"  ✓ 要約完了: {summary[:80]}...")

        # データベースに保存
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE discussions
            SET content = ?,
                summary = ?,
                updated_at = ?
            WHERE id = ?
        """, (content, summary, now, disc_id))

        conn.commit()
        summarized_count += 1
        print(f"  💾 保存完了\n")

    conn.close()

    print(f"{'='*60}")
    print(f"✅ 完了: {summarized_count}件要約、{skipped_count}件スキップ")
    print(f"{'='*60}\n")


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description='ディスカッション要約スクリプト')
    parser.add_argument('competition_id', help='コンペティションID（例: titanic）')
    parser.add_argument('--max', type=int, default=10, help='要約する最大ディスカッション数（デフォルト: 10）')

    args = parser.parse_args()

    summarize_discussion_for_competition(
        comp_id=args.competition_id,
        max_discussions=args.max
    )


if __name__ == "__main__":
    main()
