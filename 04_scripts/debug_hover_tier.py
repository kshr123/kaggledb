#!/usr/bin/env python3
"""
投稿者にマウスオーバーして称号（tier）を取得するテスト
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
import time

url = "https://www.kaggle.com/competitions/titanic/discussion"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    # ディスカッションアイテムを取得
    items = page.locator('li.MuiListItem-root').all()

    print(f"Found {len(items)} discussion items\n")

    # 最初の5件でテスト
    for i, item in enumerate(items[:5], 1):
        print(f"\n{'='*60}")
        print(f"Discussion {i}")
        print('='*60)

        try:
            # タイトルを取得
            title_link = item.locator('a[href*="/discussion/"]').first
            if title_link.count() > 0:
                title = title_link.text_content()
                print(f"Title: {title}")

            # 投稿者リンクを取得
            author_links = item.locator('a[target="_blank"]').all()

            for author_link in author_links:
                # リンクのテキストを確認（プロフィールリンクかどうか）
                href = author_link.get_attribute('href')
                if href and href.startswith('/') and 'discussion' not in href:
                    aria_label = author_link.get_attribute('aria-label')

                    if aria_label and 'profile' in aria_label:
                        author_name = aria_label.split("'s profile")[0] if "'s profile" in aria_label else "Unknown"
                        print(f"\nAuthor: {author_name}")
                        print(f"Link: {href}")

                        # マウスオーバー
                        print("Hovering over author link...")
                        author_link.hover()

                        # ツールチップやポップアップが表示されるまで待機
                        time.sleep(2)

                        # ページのHTMLを取得して称号を探す
                        # ツールチップは通常、body直下に追加される
                        page_content = page.content()

                        # "Master", "Grandmaster", "Expert", "Contributor" などの称号を探す
                        tiers = ['Grandmaster', 'Master', 'Expert', 'Contributor', 'Novice']
                        found_tier = None

                        for tier in tiers:
                            if tier.lower() in page_content.lower():
                                # より正確に称号を特定（ツールチップ内のテキスト）
                                # MUIのTooltipやPopoverを探す
                                tooltip = page.locator('[role="tooltip"]')
                                if tooltip.count() > 0:
                                    tooltip_text = tooltip.first.text_content()
                                    if tier.lower() in tooltip_text.lower():
                                        found_tier = tier
                                        break

                        if found_tier:
                            print(f"✅ Tier found: {found_tier}")
                        else:
                            print("❌ No tier found in tooltip")

                            # デバッグ: ツールチップのHTMLを確認
                            tooltip = page.locator('[role="tooltip"]')
                            if tooltip.count() > 0:
                                print(f"\nTooltip content:")
                                print(tooltip.first.text_content())

                        # ホバーを解除
                        page.mouse.move(0, 0)
                        time.sleep(1)
                        break

        except Exception as e:
            print(f"Error: {e}")
            continue

    print("\n\nPress Enter to close browser...")
    input()
    browser.close()
