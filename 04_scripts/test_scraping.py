#!/usr/bin/env python3
"""
スクレイピング機能テストスクリプト

2-3件のコンペでスクレイピングとキャッシュをテスト
"""

import sys
import os
import argparse

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from app.services.scraper_service import ScraperService


def main():
    parser = argparse.ArgumentParser(description="スクレイピング機能テスト")
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="ブラウザを表示して実行（デフォルト: ヘッドレスモード）"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="テストするコンペ数（デフォルト: 3）"
    )
    parser.add_argument(
        "--cache-ttl",
        type=int,
        default=1,
        help="キャッシュ有効期限（日数、デフォルト: 1）"
    )

    args = parser.parse_args()

    # デフォルトは headless=True, --show-browser で False に
    headless = not args.show_browser

    print("=" * 60)
    print("スクレイピング機能テスト")
    print("=" * 60)
    print(f"モード: {'ヘッドレス' if headless else 'ブラウザ表示'}")
    print(f"キャッシュTTL: {args.cache_ttl}日")

    # テスト対象のコンペティション
    all_competitions = [
        'titanic',           # 定番・安定
        'house-prices',      # 定番・安定
        'digit-recognizer',  # 定番・安定
    ]
    test_competitions = all_competitions[:args.limit]

    # スクレイピングサービス取得
    if not headless:
        print("\n⚠️  ブラウザウィンドウが表示されます...")

    scraper = ScraperService(cache_ttl_days=args.cache_ttl, headless=headless)

    print(f"\n📋 テスト対象: {len(test_competitions)}件")
    print("-" * 60)

    # 各コンペをスクレイピング
    for i, comp_id in enumerate(test_competitions, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(test_competitions)}] {comp_id}")
        print('='*60)

        # スクレイピング実行
        result = scraper.get_competition_details(comp_id)

        if result:
            print(f"\n✅ 成功！")
            print(f"\n取得したフィールド:")
            for key, value in result.items():
                if key == 'scraped_at':
                    print(f"  - {key}: {value}")
                elif isinstance(value, str):
                    # 長いテキストは最初の200文字のみ表示
                    preview = value[:200] + '...' if len(value) > 200 else value
                    print(f"  - {key}: {preview}")
                else:
                    print(f"  - {key}: {value}")

            # キャッシュテスト（2回目は即座に返る）
            print(f"\n🔄 キャッシュテスト（2回目の取得）")
            result2 = scraper.get_competition_details(comp_id)
            if result2:
                print(f"✅ キャッシュから取得成功！")
        else:
            print(f"❌ スクレイピング失敗")

        print("-" * 60)

    # サマリー
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)
    print("\n次のステップ:")
    print("  1. キャッシュが正しく動作していることを確認")
    print("  2. スクレイピングデータをLLMで処理して要約生成")
    print("  3. enrich_competitions.py を更新してスクレイピング対応")


if __name__ == "__main__":
    main()
