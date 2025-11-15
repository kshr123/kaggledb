#!/usr/bin/env python3
"""
Kaggle コンペティションページの HTML 構造を調査するスクリプト
"""

import requests
from bs4 import BeautifulSoup
import sys


def inspect_page(comp_id: str):
    """
    Kaggle コンペティションページの HTML 構造を調査

    Args:
        comp_id: コンペティション ID
    """
    url = f"https://www.kaggle.com/competitions/{comp_id}"

    print("=" * 80)
    print(f"Kaggle ページ構造調査: {comp_id}")
    print("=" * 80)
    print(f"URL: {url}\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    }

    try:
        print("⏳ ページを取得中...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ ステータスコード: {response.status_code}\n")

        soup = BeautifulSoup(response.text, 'lxml')

        # HTML を保存
        output_file = f"/tmp/{comp_id}_page.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"📄 HTML 保存: {output_file}\n")

        # 主要な要素を探索
        print("=" * 80)
        print("主要な要素の探索")
        print("=" * 80)

        # タイトル
        title = soup.find('title')
        if title:
            print(f"\n📌 ページタイトル:\n{title.get_text(strip=True)}\n")

        # すべての div のクラスを調査
        print("\n📦 div 要素のクラス名（最初の50個）:")
        print("-" * 80)
        divs = soup.find_all('div', class_=True)
        unique_classes = set()
        for div in divs[:50]:
            classes = ' '.join(div.get('class', []))
            if classes:
                unique_classes.add(classes)

        for cls in sorted(list(unique_classes))[:30]:
            print(f"  - {cls}")

        # id 属性を持つ要素
        print("\n🆔 id 属性を持つ要素（最初の30個）:")
        print("-" * 80)
        elements_with_id = soup.find_all(id=True)
        for elem in elements_with_id[:30]:
            print(f"  - <{elem.name} id=\"{elem.get('id')}\">")

        # script タグ（JSON データが含まれている可能性）
        print("\n📜 script タグ（JSON データを探索）:")
        print("-" * 80)
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts[:10]):
            script_text = script.get_text()[:200]
            if 'competition' in script_text.lower() or 'description' in script_text.lower():
                print(f"  Script {i+1}: {script_text}...")

        print("\n" + "=" * 80)
        print("次のステップ:")
        print("=" * 80)
        print(f"1. 保存された HTML ファイルを開く: {output_file}")
        print("2. ブラウザの開発者ツールで実際のページを検証")
        print("3. 正しいセレクターを特定")
        print("4. scraper_service.py の _extract_* メソッドを修正")

    except requests.RequestException as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kaggle ページの HTML 構造を調査")
    parser.add_argument(
        "comp_id",
        type=str,
        default="titanic",
        nargs="?",
        help="コンペティション ID（デフォルト: titanic）"
    )

    args = parser.parse_args()
    inspect_page(args.comp_id)
