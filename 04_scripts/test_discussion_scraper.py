#!/usr/bin/env python3
"""
ディスカッションスクレイピングのテストスクリプト

小規模なサンプルでget_discussions()の動作確認を行います。
"""

import sys
import os

# バックエンドのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from app.services.scraper_service import get_scraper_service
import json


def test_discussion_scraping():
    """ディスカッションスクレイピングのテスト"""

    # テスト対象のコンペティション（少数）
    test_competitions = [
        'titanic',  # 最も有名で議論が多いコンペ
    ]

    print("=" * 60)
    print("ディスカッションスクレイピング テスト")
    print("=" * 60)
    print()

    scraper = get_scraper_service()

    for comp_id in test_competitions:
        print(f"\n{'=' * 60}")
        print(f"コンペティション: {comp_id}")
        print(f"{'=' * 60}\n")

        # ディスカッション取得（1ページのみ）
        discussions = scraper.get_discussions(
            comp_id=comp_id,
            max_pages=1,
            force_refresh=True  # キャッシュを使わず新規取得
        )

        if discussions:
            print(f"\n✅ 取得成功: {len(discussions)}件のディスカッション")
            print("\n--- サンプル（最初の3件）---")

            for i, disc in enumerate(discussions[:3], 1):
                print(f"\n【{i}】 {disc['title']}")
                print(f"  作成者: {disc.get('author', 'N/A')}")
                print(f"  投票数: {disc.get('vote_count', 0)}")
                print(f"  コメント数: {disc.get('comment_count', 0)}")
                print(f"  カテゴリ: {disc.get('category', 'N/A')}")
                print(f"  ピン留め: {disc.get('is_pinned', False)}")
                print(f"  URL: {disc['url']}")

            # データ構造の検証
            print("\n--- データ構造検証 ---")
            required_fields = ['title', 'url', 'author', 'vote_count',
                             'comment_count', 'category', 'is_pinned']

            sample = discussions[0]
            missing_fields = [field for field in required_fields
                            if field not in sample]

            if missing_fields:
                print(f"⚠️  不足しているフィールド: {missing_fields}")
            else:
                print("✅ すべての必須フィールドが存在します")

            # JSON形式で出力（最初の1件）
            print("\n--- JSON形式（1件目）---")
            print(json.dumps(discussions[0], ensure_ascii=False, indent=2))

        else:
            print(f"❌ 取得失敗: {comp_id}")

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    test_discussion_scraping()
