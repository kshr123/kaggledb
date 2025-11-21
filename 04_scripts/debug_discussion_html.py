#!/usr/bin/env python3
"""
ディスカッションページのHTML構造を確認するデバッグスクリプト
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time


def debug_discussion_page():
    """ディスカッションページのHTML構造を確認"""

    comp_id = 'titanic'
    url = f"https://www.kaggle.com/competitions/{comp_id}/discussion"

    print(f"URL: {url}\n")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("ページに移動中...")
            response = page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"ステータスコード: {response.status}")

            print("JavaScriptレンダリング待機中...")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # HTMLをファイルに保存
            output_file = '/tmp/kaggle_discussion_debug.html'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\n✅ HTML保存: {output_file}")

            # ページタイトル
            print(f"\nページタイトル: {page.title()}")

            # いくつかの候補セレクタを試す
            selectors_to_test = [
                '[data-testid="discussion-list-item"]',
                '.discussion-list-item',
                '[class*="discussion"]',
                '[class*="Discussion"]',
                'article',
                '[role="article"]',
                'li[class*="list"]',
                'div[class*="topic"]',
            ]

            print("\n--- セレクタテスト ---")
            for selector in selectors_to_test:
                elements = soup.select(selector)
                print(f"{selector}: {len(elements)}件")
                if elements:
                    print(f"  最初の要素のクラス: {elements[0].get('class')}")

            # リンクを探す
            discussion_links = soup.select('a[href*="/discussion/"]')
            print(f"\n--- ディスカッションリンク ---")
            print(f"見つかったリンク: {len(discussion_links)}件")

            if discussion_links:
                print("\n最初の5件:")
                for i, link in enumerate(discussion_links[:5], 1):
                    print(f"{i}. {link.get_text(strip=True)[:60]}...")
                    print(f"   href: {link.get('href')}")
                    print(f"   親要素: {link.parent.name}")
                    print(f"   親要素クラス: {link.parent.get('class')}")
                    print()

            browser.close()

            print(f"\n詳細はHTMLファイルを確認してください: {output_file}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_discussion_page()
