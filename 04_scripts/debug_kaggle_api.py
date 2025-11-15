#!/usr/bin/env python3
"""
Kaggle APIのレスポンス構造を調査するデバッグスクリプト
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from kaggle.api.kaggle_api_extended import KaggleApi

def main():
    print("=" * 60)
    print("Kaggle API レスポンス構造調査")
    print("=" * 60)

    api = KaggleApi()
    api.authenticate()

    # 1. competitions_list() のレスポンス確認
    print("\n1. competitions_list() のレスポンス:")
    print("-" * 60)
    competitions = api.competitions_list(page=1)
    if competitions:
        comp = competitions[0]
        print(f"コンペ: {comp.title}")
        print(f"ID: {comp.ref}")
        print(f"\n利用可能な属性:")
        for attr in sorted(dir(comp)):
            if not attr.startswith('_'):
                value = getattr(comp, attr, None)
                if not callable(value):
                    print(f"  {attr}: {value}")

    # 2. competition_view() のレスポンス確認
    print("\n\n2. competition_view() のレスポンス:")
    print("-" * 60)
    try:
        # Titanicコンペで詳細を取得
        detail = api.competition_view('titanic')
        print(f"コンペ: {detail.title}")
        print(f"ID: {detail.ref}")
        print(f"\n利用可能な属性:")
        for attr in sorted(dir(detail)):
            if not attr.startswith('_'):
                value = getattr(detail, attr, None)
                if not callable(value):
                    print(f"  {attr}: {value}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 3. 詳細説明フィールドの確認
    print("\n\n3. 詳細説明フィールドの確認:")
    print("-" * 60)
    print(f"  description (短い): {getattr(comp, 'description', 'NOT FOUND')}")

    # より詳しい説明フィールドを探す
    for attr in ['detailed_description', 'overview', 'summary', 'full_description']:
        value = getattr(comp, attr, None)
        if value:
            print(f"  {attr}: {value[:200]}...")  # 最初の200文字のみ表示

if __name__ == "__main__":
    main()
