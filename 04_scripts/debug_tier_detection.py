#!/usr/bin/env python3
"""
称号検出のデバッグスクリプト

Titanicのディスカッションページを開いて、
実際にどんなHTML要素があるかを調査する
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
import time

def debug_tier_detection():
    """ディスカッションページのHTML構造を調査"""

    url = "https://www.kaggle.com/competitions/titanic/discussion"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # ブラウザを表示
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

        print(f"\n✅ {len(discussion_items)}件のディスカッションを検出")

        # 最初の3件を詳しく調査
        for idx, item in enumerate(discussion_items[:3], 1):
            print(f"\n{'='*60}")
            print(f"ディスカッション #{idx}")
            print(f"{'='*60}")

            # タイトル
            title_link = item.locator('a[href*="/discussion/"]').first
            if title_link.count() > 0:
                title = title_link.text_content().strip()
                print(f"タイトル: {title}")

            # 投稿者リンクを探す
            author_links = item.locator('a[target="_blank"]').all()

            for author_link in author_links:
                link_href = author_link.get_attribute('href')
                if link_href and link_href.startswith('/') and 'discussion' not in link_href:
                    aria_label = author_link.get_attribute('aria-label')
                    if aria_label and "'s profile" in aria_label:
                        author = aria_label.split("'s profile")[0]
                        print(f"\n投稿者: {author}")
                        print(f"プロフィールリンク: {link_href}")

                        # ホバー前のHTML
                        print("\n--- ホバー前のHTML (一部) ---")
                        item_html = item.inner_html()
                        print(item_html[:500])

                        # ホバーする
                        print("\n🖱️  投稿者リンクにホバー...")
                        author_link.hover(timeout=5000)
                        time.sleep(3)  # 十分待つ

                        # ホバー後に表示される全要素を調査
                        print("\n--- ホバー後の調査 ---")

                        # ページ全体から新しく表示された要素を探す
                        # 1. role="tooltip"
                        tooltips = page.locator('[role="tooltip"]').all()
                        print(f"[role=tooltip]: {len(tooltips)}個")
                        for i, tt in enumerate(tooltips):
                            if tt.is_visible():
                                print(f"  Tooltip {i+1}: {tt.text_content()[:200]}")

                        # 2. MuiTooltip
                        mui_tooltips = page.locator('.MuiTooltip-tooltip').all()
                        print(f"[.MuiTooltip-tooltip]: {len(mui_tooltips)}個")
                        for i, tt in enumerate(mui_tooltips):
                            if tt.is_visible():
                                print(f"  MuiTooltip {i+1}: {tt.text_content()[:200]}")

                        # 3. Popover
                        popovers = page.locator('[role="dialog"], [role="menu"], .MuiPopover-root, .MuiPopper-root').all()
                        print(f"[Popover/Dialog/Menu]: {len(popovers)}個")
                        for i, pop in enumerate(popovers):
                            if pop.is_visible():
                                print(f"  Popover {i+1}: {pop.text_content()[:200]}")

                        # 4. 任意の新しく表示された div
                        print("\n--- 可視divの一覧（最大10個） ---")
                        all_divs = page.locator('div[style*="position"]').all()
                        for i, div in enumerate(all_divs[:10]):
                            if div.is_visible():
                                text = div.text_content()
                                if text and len(text.strip()) > 0:
                                    print(f"Div {i+1}: {text[:100]}")

                        # 5. 「Master」「Grandmaster」というテキストを含む全要素
                        print("\n--- 称号キーワードを含む要素 ---")
                        tier_keywords = ['Master', 'Grandmaster', 'Expert', 'Contributor']
                        for keyword in tier_keywords:
                            elements = page.locator(f'text={keyword}').all()
                            if elements:
                                print(f"\n'{keyword}' を含む要素: {len(elements)}個")
                                for i, elem in enumerate(elements[:3]):
                                    if elem.is_visible():
                                        print(f"  {i+1}. タグ: {elem.evaluate('el => el.tagName')}")
                                        print(f"     テキスト: {elem.text_content()[:100]}")
                                        print(f"     HTML: {elem.inner_html()[:200]}")

                        # ホバーを解除
                        page.mouse.move(0, 0)
                        time.sleep(1)

                        break

        print(f"\n{'='*60}")
        print("調査完了。10秒後にブラウザを閉じます...")
        print(f"{'='*60}\n")
        time.sleep(10)

        browser.close()


if __name__ == "__main__":
    debug_tier_detection()
