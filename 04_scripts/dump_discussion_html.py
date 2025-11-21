#!/usr/bin/env python3
"""
ディスカッションアイテムのHTML構造をダンプ
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
import time

def dump_discussion_html():
    """ディスカッションアイテムのHTMLを出力"""

    url = "https://www.kaggle.com/competitions/titanic/discussion"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"\n🌐 ページを開く: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # 最初のディスカッションアイテムを取得
        discussion_items = page.locator('li.MuiListItem-root').all()

        if not discussion_items:
            print("❌ ディスカッションが見つかりません")
            browser.close()
            return

        print(f"\n✅ {len(discussion_items)}件のディスカッションを検出\n")

        # 10-12件目のHTMLをダンプ（最初の方はナビリンクなのでスキップ）
        for idx, item in enumerate(discussion_items[10:12], 11):
            print(f"{'='*80}")
            print(f"ディスカッション #{idx} の完全なHTML")
            print(f"{'='*80}\n")

            html = item.inner_html()
            print(html)

            print(f"\n{'='*80}")
            print(f"ディスカッション #{idx} のテキスト")
            print(f"{'='*80}\n")

            text = item.inner_text()
            print(text)

            print(f"\n{'='*80}\n")

        browser.close()


if __name__ == "__main__":
    dump_discussion_html()
