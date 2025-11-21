#!/usr/bin/env python3
"""
失敗したコンペ2件を再取得
"""

import sys
import os

# パス設定
script_dir = os.path.dirname(__file__)
backend_dir = os.path.join(script_dir, '..', '02_backend')
sys.path.insert(0, backend_dir)
sys.path.insert(0, script_dir)

# 元のスクリプトから関数をインポート
from enrich_competitions_with_details import enrich_competition, save_to_db
from app.services.scraper_service import get_scraper_service
from app.services.llm_service import get_llm_service

# 失敗した2件のコンペID
FAILED_IDS = [
    'birdsong-recognition',
    'learning-equality-curriculum-recommendations'
]


def main():
    print("=" * 60)
    print("失敗したコンペ2件の再取得")
    print("=" * 60)

    scraper = get_scraper_service()
    llm_service = get_llm_service()

    success_count = 0
    fail_count = 0

    for i, comp_id in enumerate(FAILED_IDS, 1):
        print(f"\n進捗: {i}/{len(FAILED_IDS)}\n")

        # Step 1 & 2: スクレイピング + LLM処理
        enriched_data = enrich_competition(comp_id, scraper, llm_service)

        if not enriched_data:
            fail_count += 1
            continue

        # Step 3: DB保存
        if save_to_db(comp_id, enriched_data):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)
    print(f"成功: {success_count}件")
    print(f"失敗: {fail_count}件")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
