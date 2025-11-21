#!/usr/bin/env python3
"""
ディスカッションページで金メダリストの表示を確認
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://www.kaggle.com/competitions/titanic/discussion"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # ブラウザを表示
    page = browser.new_page()

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    # ディスカッションリストを取得
    discussion_items = soup.select('li.MuiListItem-root')
    valid_items = [item for item in discussion_items
                  if item.select_one('.km-listitem--medium')]

    print(f"Found {len(valid_items)} discussions\n")

    # 最初の5件を詳しく調査
    for i, item in enumerate(valid_items[:5], 1):
        print(f"\n{'='*60}")
        print(f"Discussion {i}")
        print('='*60)

        # タイトル
        title_link = item.select_one('a[href*="/discussion/"]')
        if title_link:
            title_div = item.select_one('.sc-bylIJf')
            title = title_div.get_text(strip=True) if title_div else title_link.get_text(strip=True)
            print(f"Title: {title}")

        # 作成者情報周辺のHTML全体を出力
        author_link = item.select_one('a[href^="/"][href*="/"][target="_blank"]')
        if author_link:
            print(f"\nAuthor link HTML:")
            print(author_link.prettify())

            # 作成者の親要素を確認（メダル情報があるかも）
            parent = author_link.parent
            if parent:
                print(f"\nParent element:")
                print(parent.prettify())

        # メダル関連のアイコンを探す
        # 一般的なパターン: 'medal', 'gold', 'badge' などのクラス名やテキスト
        medals = item.find_all(string=lambda x: x and ('medal' in x.lower() or 'gold' in x.lower()))
        if medals:
            print(f"\nMedal-related text found: {medals}")

        # SVGアイコンを確認
        svgs = item.find_all('svg')
        if svgs:
            print(f"\nFound {len(svgs)} SVG icons")
            for svg in svgs[:3]:  # 最初の3個だけ
                # aria-labelやtitleを確認
                if svg.get('aria-label'):
                    print(f"  SVG aria-label: {svg['aria-label']}")
                if svg.find('title'):
                    print(f"  SVG title: {svg.find('title').text}")

    print("\n\nPress Enter to close browser...")
    input()
    browser.close()
