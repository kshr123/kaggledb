#!/usr/bin/env python3
"""
スクレイピング機能テストスクリプト

2-3件のコンペでスクレイピングとキャッシュをテスト
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from app.services.scraper_service import get_scraper_service


def main():
    print("=" * 60)
    print("スクレイピング機能テスト")
    print("=" * 60)

    # テスト対象のコンペティション
    test_competitions = [
        'titanic',           # 定番・安定
        'house-prices',      # 定番・安定
        'digit-recognizer',  # 定番・安定
    ]

    # スクレイピングサービス取得
    scraper = get_scraper_service(cache_ttl_days=1)

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
