#!/usr/bin/env python3
"""
解法収集スクリプト

コンペティションのディスカッションから解法（Solution）を識別して
solutionsテーブルに保存します。
"""
import sys
import os
import re

# プロジェクトルートからの相対パス
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, '02_backend')
sys.path.insert(0, backend_path)

import sqlite3
from datetime import datetime
from app.config import DATABASE_PATH
from app.services.scraper_service import get_scraper_service


def is_solution_discussion(title: str) -> tuple[bool, int | None]:
    """
    タイトルから解法ディスカッションかどうかを判定

    Args:
        title: ディスカッションタイトル

    Returns:
        (is_solution, rank): 解法かどうかと順位（あれば）
    """
    title_lower = title.lower()

    # 解法を示すキーワード
    solution_keywords = [
        'solution',
        'approach',
        'write-up',
        'writeup',
        '解法',
        'our solution',
        'my solution'
    ]

    # 順位を示すパターン
    rank_patterns = [
        r'(\d+)(?:st|nd|rd|th)\s+place',  # 1st place, 2nd place等
        r'#(\d+)\s+solution',              # #1 solution等
        r'rank\s+(\d+)',                   # rank 1等
    ]

    # 解法キーワードチェック
    has_solution_keyword = any(keyword in title_lower for keyword in solution_keywords)

    # 順位抽出
    rank = None
    for pattern in rank_patterns:
        match = re.search(pattern, title_lower)
        if match:
            rank = int(match.group(1))
            break

    # 順位があれば確実に解法
    if rank:
        return True, rank

    # 解法キーワードがあれば解法
    if has_solution_keyword:
        return True, None

    return False, None


def collect_solutions_for_competition(comp_id: str, max_discussions: int = 50):
    """
    コンペの解法ディスカッションを収集

    Args:
        comp_id: コンペティションID
        max_discussions: 最大取得ディスカッション数
    """
    print(f"\n{'='*70}")
    print(f"解法収集: {comp_id}")
    print(f"{'='*70}\n")

    scraper = get_scraper_service()

    # ディスカッション一覧を取得（既存のスクレイパーを使用）
    max_pages = (max_discussions + 19) // 20  # 1ページ20件として計算
    discussions = scraper.get_discussions(
        comp_id=comp_id,
        max_pages=max_pages,
        force_refresh=False
    )

    if not discussions:
        print("❌ ディスカッションの取得に失敗しました")
        return

    print(f"\n取得完了: {len(discussions)}件のディスカッション")

    # 解法をフィルター
    solutions = []
    for disc in discussions:
        is_solution, rank = is_solution_discussion(disc['title'])
        if is_solution:
            solutions.append({
                **disc,
                'rank': rank,
                'type': 'discussion'
            })

    print(f"解法候補: {len(solutions)}件\n")

    if not solutions:
        print("❌ 解法が見つかりませんでした")
        return

    # データベースに保存
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    saved_count = 0
    updated_count = 0

    for sol in solutions:
        # 既存チェック（URLで重複確認）
        cursor.execute(
            "SELECT id FROM solutions WHERE competition_id = ? AND url = ?",
            (comp_id, sol['url'])
        )
        existing = cursor.fetchone()

        now = datetime.now().isoformat()

        # メダル判定（1-3位）
        medal = None
        if sol['rank']:
            if sol['rank'] == 1:
                medal = 'gold'
            elif sol['rank'] == 2:
                medal = 'silver'
            elif sol['rank'] == 3:
                medal = 'bronze'

        if existing:
            # 更新
            cursor.execute("""
                UPDATE solutions
                SET title = ?,
                    author = ?,
                    author_tier = ?,
                    tier_color = ?,
                    type = ?,
                    medal = ?,
                    rank = ?,
                    vote_count = ?,
                    comment_count = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                sol['title'],
                sol.get('author'),
                sol.get('author_tier'),
                sol.get('tier_color'),
                sol['type'],
                medal,
                sol['rank'],
                sol['vote_count'],
                sol['comment_count'],
                now,
                existing[0]
            ))
            updated_count += 1
            print(f"✓ 更新: {sol['title'][:60]}... (👍 {sol['vote_count']})")
        else:
            # 新規作成
            cursor.execute("""
                INSERT INTO solutions (
                    competition_id,
                    title,
                    author,
                    author_tier,
                    tier_color,
                    url,
                    type,
                    medal,
                    rank,
                    vote_count,
                    comment_count,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comp_id,
                sol['title'],
                sol.get('author'),
                sol.get('author_tier'),
                sol.get('tier_color'),
                sol['url'],
                sol['type'],
                medal,
                sol['rank'],
                sol['vote_count'],
                sol['comment_count'],
                now,
                now
            ))
            saved_count += 1
            print(f"✓ 保存: {sol['title'][:60]}... (👍 {sol['vote_count']})")

    conn.commit()
    conn.close()

    print(f"\n{'='*70}")
    print(f"✅ 完了: 新規{saved_count}件、更新{updated_count}件")
    print(f"{'='*70}\n")


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description='解法収集スクリプト')
    parser.add_argument('competition_id', help='コンペティションID')
    parser.add_argument('--max', type=int, default=50, help='最大取得数（デフォルト: 50）')

    args = parser.parse_args()

    collect_solutions_for_competition(
        comp_id=args.competition_id,
        max_discussions=args.max
    )


if __name__ == "__main__":
    main()
