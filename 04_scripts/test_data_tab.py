#!/usr/bin/env python3
"""
Data タブスクレイピングテストスクリプト

Data タブからデータセット情報を取得し、LLMで抽出する機能をテスト
"""

import sys
import os
import json

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from app.services.scraper_service import get_scraper_service
from app.services.llm_service import get_llm_service


def main():
    print("=" * 60)
    print("Data タブスクレイピングテスト")
    print("=" * 60)

    # テスト対象のコンペティション（有名なもの）
    test_comp_id = "titanic"

    # サービス初期化
    try:
        scraper = get_scraper_service()
        llm = get_llm_service()
        print("✅ サービス初期化成功")
    except Exception as e:
        print(f"❌ サービス初期化失敗: {e}")
        return

    print(f"\n📋 テスト対象: {test_comp_id}")
    print("-" * 60)

    # 1. Data タブのスクレイピング
    print("\n🌐 Data タブをスクレイピング中...")
    data_tab_content = scraper.get_tab_content(test_comp_id, tab="data")

    if not data_tab_content:
        print("❌ Data タブのスクレイピング失敗")
        return

    print(f"✅ スクレイピング成功: {len(data_tab_content.get('full_text', ''))} 文字取得")

    # テキストの一部を表示（確認用）
    text_preview = data_tab_content['full_text'][:500]
    print(f"\n📄 取得テキストのプレビュー:")
    print(f"{text_preview}...")

    # 2. LLMでデータセット情報を抽出
    print(f"\n🤖 LLMでデータセット情報を抽出中...")
    dataset_info = llm.extract_dataset_info(
        data_text=data_tab_content['full_text'],
        title=test_comp_id
    )

    if dataset_info:
        print(f"✅ データセット情報抽出成功")
        print(f"\n📊 抽出結果:")
        print(json.dumps(dataset_info, ensure_ascii=False, indent=2))

        # 各フィールドの詳細
        print(f"\n📁 ファイル一覧 ({len(dataset_info.get('files', []))}件):")
        for file in dataset_info.get('files', []):
            print(f"  - {file}")

        if dataset_info.get('total_size'):
            print(f"\n💾 データセット全体サイズ: {dataset_info['total_size']}")

        if dataset_info.get('description'):
            print(f"\n📝 データ概要:")
            print(f"  {dataset_info['description']}")

        if dataset_info.get('features'):
            print(f"\n🔧 主要な特徴量 ({len(dataset_info['features'])}件):")
            for feature in dataset_info['features']:
                print(f"  - {feature}")
    else:
        print("❌ データセット情報抽出失敗")

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
