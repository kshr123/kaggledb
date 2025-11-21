#!/usr/bin/env python3
"""
Kaggle Rankings ページのHTML構造をダンプ
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
import time

def dump_rankings_html():
    """ランキングページのHTMLを出力"""

    url = "https://www.kaggle.com/rankings"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"\n🌐 ページを開く: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # テーブル行を取得
        rows = page.locator('table tbody tr').all()

        if not rows:
            print("❌ テーブル行が見つかりません")
            browser.close()
            return

        print(f"\n✅ {len(rows)}行のランキングを検出\n")

        # 最初の3行のHTMLをダンプ
        for idx, row in enumerate(rows[:3], 1):
            print(f"{'='*80}")
            print(f"行 #{idx} の完全なHTML")
            print(f"{'='*80}\n")

            html = row.inner_html()
            print(html)

            print(f"\n{'='*80}")
            print(f"行 #{idx} のテキスト")
            print(f"{'='*80}\n")

            text = row.inner_text()
            print(text)

            print(f"\n{'='*80}\n")

        print("10秒後にブラウザを閉じます...")
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    dump_rankings_html()
