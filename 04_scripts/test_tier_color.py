#!/usr/bin/env python3
"""
Tier Color抽出のテスト
"""

from playwright.sync_api import sync_playwright
import time

def test_tier_color_extraction():
    """ディスカッション一覧ページからTier色を抽出"""

    url = "https://www.kaggle.com/competitions/titanic/discussion?sort=votes"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"\n🌐 アクセス: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # ディスカッションアイテムを取得
        discussion_items = page.locator('div[role="list"] > div').all()

        print(f"\n📋 ディスカッションアイテム数: {len(discussion_items)}")

        # 最初の5件を詳細に調査
        for idx, item in enumerate(discussion_items[:5], 1):
            print(f"\n{'='*60}")
            print(f"アイテム {idx}")
            print('='*60)

            # タイトル
            title_link = item.locator('a[href*="/discussion/"]').first
            if title_link.count() > 0:
                title = title_link.text_content().strip()
                print(f"タイトル: {title[:50]}...")

            # 投稿者情報
            author_links = item.locator('a[target="_blank"]').all()
            print(f"投稿者リンク数: {len(author_links)}")

            for al_idx, author_link in enumerate(author_links):
                aria_label = author_link.get_attribute('aria-label')
                print(f"  リンク{al_idx}: aria-label = {aria_label}")

            # SVG要素を探す
            svg_elements = item.locator('svg').all()
            print(f"SVG要素数: {len(svg_elements)}")

            for svg_idx, svg in enumerate(svg_elements):
                print(f"\n  SVG {svg_idx}:")

                # SVG全体のHTML
                svg_html = svg.evaluate("el => el.outerHTML")
                print(f"    HTML: {svg_html[:200]}...")

                # circle要素を探す
                circles = svg.locator('circle').all()
                print(f"    Circle要素数: {len(circles)}")

                for c_idx, circle in enumerate(circles):
                    style = circle.get_attribute('style')
                    stroke = circle.get_attribute('stroke')
                    print(f"      Circle {c_idx}: style={style}, stroke={stroke}")

            print()

        # スクリーンショット
        page.screenshot(path='/tmp/titanic_discussions.png')
        print("\n📸 スクリーンショット保存: /tmp/titanic_discussions.png")

        # 10秒待機（目視確認用）
        print("\n⏱️  10秒待機中（ブラウザで確認してください）...")
        page.wait_for_timeout(10000)

        browser.close()

if __name__ == "__main__":
    test_tier_color_extraction()
