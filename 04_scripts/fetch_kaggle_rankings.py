#!/usr/bin/env python3
"""
Kaggle Competition Rankings スクレイパー

Grandmaster と Master のリストを取得してJSONファイルに保存
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

from playwright.sync_api import sync_playwright
import time
import json

def fetch_competition_rankings(max_pages=20):
    """
    Competition RankingsからGrandmaster/Masterを取得

    Args:
        max_pages: 取得する最大ページ数（デフォルト20ページ）

    Returns:
        dict: {'grandmasters': [...], 'masters': [...]}
    """

    base_url = "https://www.kaggle.com/rankings"

    grandmasters = set()
    masters = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"{base_url}?page={page_num}" if page_num > 1 else base_url

            print(f"\n🌐 ページ {page_num}/{max_pages}: {url}")

            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)

                # ランキングテーブルの行を取得
                rows = page.locator('table tbody tr').all()

                if not rows:
                    print(f"  ❌ ランキングが見つかりません")
                    break

                print(f"  ✅ {len(rows)}名を処理中...")

                for row in rows:
                    try:
                        # Tierを取得（img タグの alt 属性から）
                        tier_img = row.locator('img[src*="/static/images/tiers/"]').first
                        if tier_img.count() == 0:
                            continue

                        tier = tier_img.get_attribute('alt')
                        if not tier:
                            continue

                        # 名前を取得（div内のテキストから）
                        name_div = row.locator('div.sc-jRLKYd').first
                        if name_div.count() == 0:
                            continue

                        # div内のテキスト全体から名前を抽出
                        name_text = name_div.inner_text().strip()
                        # 最初の行が名前（タブや改行で分割して最初の要素）
                        name = name_text.split('\n')[0].strip().split('\t')[-1].strip()

                        if not name:
                            continue

                        # Tierに応じて分類
                        if tier.lower() == 'grandmaster':
                            grandmasters.add(name)
                            print(f"    🏆 Grandmaster: {name}")
                        elif tier.lower() == 'master':
                            masters.add(name)
                            print(f"    🥈 Master: {name}")

                    except Exception as e:
                        print(f"    ⚠️  行の解析エラー: {e}")
                        continue

                # 次のページボタンがあるかチェック
                next_button = page.locator('button[aria-label="Go to next page"]')
                if next_button.count() == 0 or not next_button.is_enabled():
                    print(f"\n  最終ページに到達しました")
                    break

                # レート制限対策
                time.sleep(1)

            except Exception as e:
                print(f"  ❌ ページ{page_num}のエラー: {e}")
                break

        browser.close()

    result = {
        'grandmasters': sorted(list(grandmasters)),
        'masters': sorted(list(masters)),
        'total': len(grandmasters) + len(masters),
        'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    return result


def save_rankings(rankings, output_file):
    """ランキングをJSONファイルに保存"""

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rankings, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 保存完了: {output_file}")
    print(f"   Grandmasters: {len(rankings['grandmasters'])}名")
    print(f"   Masters: {len(rankings['masters'])}名")
    print(f"   合計: {rankings['total']}名")


def main():
    """メイン処理"""

    print("\n" + "="*60)
    print("Kaggle Competition Rankings スクレイパー")
    print("="*60)

    # ランキング取得
    rankings = fetch_competition_rankings(max_pages=20)

    # JSONファイルに保存
    output_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        '02_backend',
        'data',
        'kaggle_rankings.json'
    )

    save_rankings(rankings, output_file)

    print("\n" + "="*60)
    print("完了")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
