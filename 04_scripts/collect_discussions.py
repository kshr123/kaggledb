#!/usr/bin/env python3
"""
ディスカッション収集スクリプト

指定したコンペティションのディスカッションをスクレイピングしてDBに保存します。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from app.config import DATABASE_PATH
from app.services.scraper_service import get_scraper_service


def save_discussions_to_db(comp_id: str, discussions: list[dict], with_content: bool = False):
    """ディスカッションをデータベースに保存"""

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    saved_count = 0
    updated_count = 0

    for disc in discussions:
        # URLからディスカッションIDを抽出
        discussion_id = disc['url'].split('/discussion/')[-1].split('#')[0]

        # 既存のレコードをチェック
        cursor.execute(
            "SELECT id FROM discussions WHERE competition_id = ? AND url = ?",
            (comp_id, disc['url'])
        )
        existing = cursor.fetchone()

        now = datetime.now().isoformat()

        if existing:
            # 更新
            if with_content and 'content' in disc:
                cursor.execute("""
                    UPDATE discussions
                    SET title = ?,
                        author = ?,
                        author_tier = ?,
                        tier_color = ?,
                        vote_count = ?,
                        comment_count = ?,
                        category = ?,
                        is_pinned = ?,
                        content = ?,
                        summary = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    disc['title'],
                    disc['author'],
                    disc.get('author_tier'),
                    disc.get('tier_color'),
                    disc['vote_count'],
                    disc['comment_count'],
                    disc['category'],
                    disc['is_pinned'],
                    disc.get('content'),
                    disc.get('summary'),
                    now,
                    existing[0]
                ))
            else:
                cursor.execute("""
                    UPDATE discussions
                    SET title = ?,
                        author = ?,
                        author_tier = ?,
                        tier_color = ?,
                        vote_count = ?,
                        comment_count = ?,
                        category = ?,
                        is_pinned = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    disc['title'],
                    disc['author'],
                    disc.get('author_tier'),
                    disc.get('tier_color'),
                    disc['vote_count'],
                    disc['comment_count'],
                    disc['category'],
                    disc['is_pinned'],
                    now,
                    existing[0]
                ))
            updated_count += 1
        else:
            # 新規作成
            if with_content and 'content' in disc:
                cursor.execute("""
                    INSERT INTO discussions (
                        competition_id,
                        title,
                        author,
                        author_tier,
                        tier_color,
                        url,
                        vote_count,
                        comment_count,
                        category,
                        is_pinned,
                        content,
                        summary,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp_id,
                    disc['title'],
                    disc['author'],
                    disc.get('author_tier'),
                    disc.get('tier_color'),
                    disc['url'],
                    disc['vote_count'],
                    disc['comment_count'],
                    disc['category'],
                    disc['is_pinned'],
                    disc.get('content'),
                    disc.get('summary'),
                    now,
                    now
                ))
            else:
                cursor.execute("""
                    INSERT INTO discussions (
                        competition_id,
                        title,
                        author,
                        author_tier,
                        tier_color,
                        url,
                        vote_count,
                        comment_count,
                        category,
                        is_pinned,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp_id,
                    disc['title'],
                    disc['author'],
                    disc.get('author_tier'),
                    disc.get('tier_color'),
                    disc['url'],
                    disc['vote_count'],
                    disc['comment_count'],
                    disc['category'],
                    disc['is_pinned'],
                    now,
                    now
                ))
            saved_count += 1

    conn.commit()
    conn.close()

    return saved_count, updated_count


def collect_discussions(comp_id: str, max_pages: int = 1, force_refresh: bool = False):
    """ディスカッションを収集してDBに保存"""

    print(f"\n{'='*60}")
    print(f"ディスカッション収集: {comp_id}")
    print(f"{'='*60}\n")

    scraper = get_scraper_service()

    # スクレイピング
    discussions = scraper.get_discussions(
        comp_id=comp_id,
        max_pages=max_pages,
        force_refresh=force_refresh
    )

    if not discussions:
        print(f"❌ ディスカッションの取得に失敗しました")
        return

    print(f"\n取得完了: {len(discussions)}件")

    # データベースに保存
    saved, updated = save_discussions_to_db(comp_id, discussions)

    print(f"\n✅ データベース保存完了:")
    print(f"  新規保存: {saved}件")
    print(f"  更新: {updated}件")
    print(f"  合計: {saved + updated}件")


def main():
    """メイン処理"""

    # テスト用の少数コンペティション
    test_competitions = [
        'titanic',  # 最も有名
    ]

    print("\n" + "="*60)
    print("ディスカッション収集スクリプト")
    print("="*60)

    for comp_id in test_competitions:
        collect_discussions(
            comp_id=comp_id,
            max_pages=1,  # 最初は1ページのみ
            force_refresh=False  # キャッシュを使用
        )

    print("\n" + "="*60)
    print("すべての収集が完了しました")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
