#!/usr/bin/env python3
"""
Playwright でレンダリング後の HTML を確認
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
import time


def test_playwright_scraping(comp_id: str = 'titanic'):
    """
    Playwright でページを取得して HTML を保存

    Args:
        comp_id: コンペティション ID
    """
    url = f"https://www.kaggle.com/competitions/{comp_id}"

    print("=" * 80)
    print(f"Playwright スクレイピングテスト: {comp_id}")
    print("=" * 80)
    print(f"URL: {url}\n")

    with sync_playwright() as p:
        # ブラウザ起動
        print("🌐 ブラウザ起動中...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ページに移動
        print("⏳ ページを取得中...")
        page.goto(url, wait_until='networkidle', timeout=30000)

        # JavaScript レンダリング完了を待機
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("✅ ページ取得完了\n")

        # レンダリング後のHTMLを取得
        html_content = page.content()

        # HTMLを保存
        output_file = f"/tmp/{comp_id}_playwright.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 HTML 保存: {output_file}")
        print(f"   サイズ: {len(html_content):,} 文字\n")

        # テキストコンテンツのサンプル表示
        print("=" * 80)
        print("ページに含まれるテキスト（最初の2000文字）:")
        print("=" * 80)
        text = page.inner_text('body')
        print(text[:2000])
        print("\n...")

        browser.close()

        print("\n" + "=" * 80)
        print("次のステップ:")
        print("=" * 80)
        print(f"1. HTML ファイルを確認: {output_file}")
        print("2. ブラウザで実際のページを開いて開発者ツールで要素を検証")
        print("3. 正しいセレクターを特定")


if __name__ == "__main__":
    test_playwright_scraping('titanic')
