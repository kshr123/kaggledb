"""
Kaggle コンペティション詳細情報スクレイピングサービス

Kaggle APIでは取得できない詳細情報をWebスクレイピングで取得
Playwright を使用して JavaScript レンダリング後のコンテンツを取得
"""

from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from datetime import datetime
import time

from .cache_service import get_cache_service


class ScraperService:
    """Kaggle コンペティションページのスクレイピング（Playwright使用）"""

    def __init__(self, cache_ttl_days: int = 1, headless: bool = True):
        """
        初期化

        Args:
            cache_ttl_days: キャッシュ有効期限（日数）デフォルト1日
            headless: ヘッドレスモードで実行するか
        """
        self.cache_service = get_cache_service()
        self.cache_ttl_days = cache_ttl_days
        self.base_url = "https://www.kaggle.com/competitions"
        self.headless = headless

    def get_competition_details(
        self,
        comp_id: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        コンペティションの詳細情報を取得

        Args:
            comp_id: コンペティション ID
            force_refresh: キャッシュを無視して再取得

        Returns:
            詳細情報の辞書（取得失敗時は None）
        """
        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(comp_id)
            if cached_data:
                return cached_data

        # スクレイピング実行
        print(f"🌐 スクレイピング開始: {comp_id}")

        try:
            scraped_data = self._scrape_competition(comp_id)

            if scraped_data:
                # キャッシュに保存
                self.cache_service.set_scraped_data(
                    comp_id,
                    scraped_data,
                    ttl_days=self.cache_ttl_days
                )
                return scraped_data
            else:
                print(f"⚠️  スクレイピング失敗: {comp_id}")
                return None

        except Exception as e:
            print(f"❌ スクレイピングエラー ({comp_id}): {e}")
            return None

    def _scrape_competition(self, comp_id: str) -> Optional[Dict[str, Any]]:
        """
        実際のスクレイピング処理（Playwright使用）

        Args:
            comp_id: コンペティション ID

        Returns:
            スクレイピングデータ
        """
        url = f"{self.base_url}/{comp_id}"

        try:
            with sync_playwright() as p:
                # ブラウザ起動
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()

                # ページに移動（タイムアウト30秒）
                response = page.goto(url, wait_until='networkidle', timeout=30000)

                # 404チェック
                if response and response.status == 404:
                    print(f"❌ コンペティションが見つかりません: {comp_id}")
                    browser.close()
                    return None

                # JavaScriptレンダリング完了を待機
                page.wait_for_load_state('networkidle')
                time.sleep(2)  # 追加の安全待機

                # ページの主要コンテンツ領域のテキストを取得
                # より簡潔なアプローチ: HTMLパースせずにテキスト直接取得
                page_text = page.inner_text('#site-content')
                browser.close()

                # 結果を返す（LLMで処理するための全テキスト）
                result = {
                    'comp_id': comp_id,
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'full_text': page_text,  # LLM処理用の全テキスト
                }

                print(f"✅ スクレイピング成功: {comp_id} ({len(page_text)} 文字)")
                return result

        except Exception as e:
            print(f"❌ スクレイピングエラー ({comp_id}): {e}")
            return None


    def get_tab_content(
        self,
        comp_id: str,
        tab: str = "",
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        指定したタブのコンテンツを取得

        Args:
            comp_id: コンペティション ID
            tab: タブ名（'data', 'discussion', 'code', 'leaderboard'）
                 空文字列の場合は Overview タブ
            force_refresh: キャッシュを無視して再取得

        Returns:
            タブコンテンツの辞書（取得失敗時は None）
        """
        # キャッシュキーにタブ名を含める
        cache_key = f"{comp_id}:{tab}" if tab else comp_id

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                return cached_data

        # スクレイピング実行
        print(f"🌐 スクレイピング開始: {comp_id}/{tab or 'overview'}")

        try:
            # URL構築
            url = f"{self.base_url}/{comp_id}/{tab}" if tab else f"{self.base_url}/{comp_id}"

            with sync_playwright() as p:
                # ブラウザ起動
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()

                # ページに移動
                response = page.goto(url, wait_until='networkidle', timeout=30000)

                # 404チェック
                if response and response.status == 404:
                    print(f"❌ ページが見つかりません: {comp_id}/{tab or 'overview'}")
                    browser.close()
                    return None

                # JavaScriptレンダリング完了を待機
                page.wait_for_load_state('networkidle')
                time.sleep(2)  # 追加の安全待機

                # ページのテキストを取得
                page_text = page.inner_text('#site-content')
                browser.close()

                # 結果を作成
                result = {
                    'comp_id': comp_id,
                    'tab': tab or 'overview',
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'full_text': page_text,
                }

                # キャッシュに保存
                self.cache_service.set_scraped_data(
                    cache_key,
                    result,
                    ttl_days=self.cache_ttl_days
                )

                print(f"✅ スクレイピング成功: {comp_id}/{tab or 'overview'} ({len(page_text)} 文字)")
                return result

        except Exception as e:
            print(f"❌ スクレイピングエラー ({comp_id}/{tab or 'overview'}): {e}")
            return None

    def _get_author_tier_from_item(self, item, author_name: str) -> Optional[str]:
        """
        ディスカッションアイテム内から称号を直接探す

        Args:
            item: ディスカッションアイテムのlocator
            author_name: 投稿者名

        Returns:
            称号（Grandmaster, Master, Expert, Contributor, Novice）またはNone
        """
        try:
            # ディスカッションアイテム全体のテキストを取得
            item_text = item.inner_text()

            # テキスト内から称号を探す
            tiers = ['Grandmaster', 'Master', 'Expert', 'Contributor', 'Novice']
            for tier in tiers:
                if tier.lower() in item_text.lower():
                    print(f"      → アイテム内テキストから称号検出: {tier}")
                    return tier

            # HTMLから称号バッジを探す（imgのalt属性やaria-labelなど）
            tier_badges = item.locator('img[alt*="tier"], [aria-label*="tier"], [title*="Grandmaster"], [title*="Master"]').all()
            for badge in tier_badges:
                alt_text = badge.get_attribute('alt') or ''
                aria_label = badge.get_attribute('aria-label') or ''
                title = badge.get_attribute('title') or ''

                combined_text = f"{alt_text} {aria_label} {title}".lower()

                for tier in tiers:
                    if tier.lower() in combined_text:
                        print(f"      → バッジから称号検出: {tier}")
                        return tier

            # SVGアイコンを探す
            svg_icons = item.locator('svg').all()
            for svg in svg_icons:
                aria_label = svg.get_attribute('aria-label') or ''
                title = svg.get_attribute('title') or ''

                combined_text = f"{aria_label} {title}".lower()

                for tier in tiers:
                    if tier.lower() in combined_text:
                        print(f"      → SVGから称号検出: {tier}")
                        return tier

        except Exception as e:
            print(f"      称号検出エラー (from item): {e}")

        return None

    def _get_tier_color_from_item(self, item) -> Optional[str]:
        """
        ディスカッションアイテム内からSVG circleのstroke colorを抽出

        Args:
            item: ディスカッションアイテムのlocator

        Returns:
            RGB色文字列（例: "rgb(235, 204, 41)"）またはNone
        """
        try:
            # SVG要素を探す
            svg_elements = item.locator('svg').all()

            for svg in svg_elements:
                # SVG内のcircle要素を探す（複数ある場合は2番目を取得）
                circles = svg.locator('circle').all()

                if len(circles) >= 2:
                    # 2番目のcircleからstroke colorを取得
                    second_circle = circles[1]
                    style_attr = second_circle.get_attribute('style')

                    if style_attr and 'stroke:' in style_attr:
                        # style属性から stroke: rgb(...) を抽出
                        import re
                        match = re.search(r'stroke:\s*(rgb\([^)]+\))', style_attr)
                        if match:
                            color = match.group(1)
                            print(f"      → SVG circle色検出: {color}")
                            return color

        except Exception as e:
            print(f"      SVG色検出エラー: {e}")

        return None

    def _get_author_tier(self, page: Page, author_link_locator) -> Optional[str]:
        """
        投稿者にホバーして称号（tier）を取得

        Args:
            page: Playwrightのページオブジェクト
            author_link_locator: 投稿者リンクのlocator

        Returns:
            称号（Grandmaster, Master, Expert, Contributor, Novice）またはNone
        """
        try:
            # マウスオーバー
            author_link_locator.hover(timeout=5000)
            time.sleep(2)  # ツールチップ表示を待機（増やした）

            # 複数の方法でツールチップを探す
            # 方法1: role="tooltip"
            tooltip = page.locator('[role="tooltip"]').first
            if tooltip.count() > 0:
                tooltip_text = tooltip.text_content(timeout=3000)
                print(f"      [tooltip] 検出: {tooltip_text[:100]}")

                # 称号を探す（優先順位順）
                tiers = ['Grandmaster', 'Master', 'Expert', 'Contributor', 'Novice']
                for tier in tiers:
                    if tier.lower() in tooltip_text.lower():
                        print(f"      → 称号検出: {tier}")
                        return tier

            # 方法2: MuiTooltipを探す
            mui_tooltip = page.locator('.MuiTooltip-tooltip').first
            if mui_tooltip.count() > 0:
                tooltip_text = mui_tooltip.text_content(timeout=3000)
                print(f"      [MuiTooltip] 検出: {tooltip_text[:100]}")

                tiers = ['Grandmaster', 'Master', 'Expert', 'Contributor', 'Novice']
                for tier in tiers:
                    if tier.lower() in tooltip_text.lower():
                        print(f"      → 称号検出: {tier}")
                        return tier

            # 方法3: data-testid="tooltip"
            testid_tooltip = page.locator('[data-testid="tooltip"]').first
            if testid_tooltip.count() > 0:
                tooltip_text = testid_tooltip.text_content(timeout=3000)
                print(f"      [testid] 検出: {tooltip_text[:100]}")

                tiers = ['Grandmaster', 'Master', 'Expert', 'Contributor', 'Novice']
                for tier in tiers:
                    if tier.lower() in tooltip_text.lower():
                        print(f"      → 称号検出: {tier}")
                        return tier

            print(f"      ツールチップ未検出")

            # ホバーを解除
            page.mouse.move(0, 0)
            time.sleep(0.5)

        except Exception as e:
            print(f"      称号取得エラー: {e}")
            import traceback
            traceback.print_exc()

        return None

    def get_discussions(
        self,
        comp_id: str,
        max_pages: int = 1,
        force_refresh: bool = False
    ) -> Optional[list[Dict[str, Any]]]:
        """
        コンペティションのディスカッション一覧を取得（1ページ分の上位ディスカッション）

        Kaggleは自動的に投票数順にソートされているため、
        1ページ目を取得すれば最も重要なディスカッションが得られる

        Args:
            comp_id: コンペティション ID
            max_pages: 取得する最大ページ数（デフォルト1ページ）
            force_refresh: キャッシュを無視して再取得

        Returns:
            ディスカッション情報のリスト
        """
        # キャッシュキー
        cache_key = f"{comp_id}:discussions:p{max_pages}"

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                print(f"✓ キャッシュから取得: {comp_id} discussions")
                return cached_data.get('discussions', cached_data)

        url = f"{self.base_url}/{comp_id}/discussion?sort=votes"
        print(f"スクレイピング: {url}")

        try:
            with sync_playwright() as p:
                browser: Browser = p.chromium.launch(headless=self.headless)
                page: Page = browser.new_page()

                all_discussions = []

                for page_num in range(1, max_pages + 1):
                    page_url = f"{url}&page={page_num}" if page_num > 1 else url

                    page.goto(page_url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)

                    # Playwrightのlocator APIを使用
                    discussion_items = page.locator('li.MuiListItem-root').all()

                    if not discussion_items:
                        print(f"  ページ{page_num}: ディスカッションが見つかりません")
                        break

                    print(f"  ページ{page_num}: {len(discussion_items)}件のディスカッションを処理中...")

                    for idx, item in enumerate(discussion_items, 1):
                        try:
                            # タイトルとURL
                            title_link = item.locator('a[href*="/discussion/"]').first
                            if title_link.count() == 0:
                                continue

                            title = title_link.text_content(timeout=3000).strip()
                            href = title_link.get_attribute('href')
                            discussion_url = f"https://www.kaggle.com{href}" if href.startswith('/') else href

                            # 投稿者情報
                            author = None
                            author_tier = None
                            tier_color = None
                            # プロフィールリンクを探す（aria-labelに's profileを含むもの）
                            author_links = item.locator('a[aria-label*="profile"]').all()

                            for author_link in author_links:
                                link_href = author_link.get_attribute('href')
                                aria_label = author_link.get_attribute('aria-label')

                                if aria_label and "'s profile" in aria_label:
                                    author = aria_label.split("'s profile")[0]
                                    print(f"    [{idx}] Author: {author}")

                                    # 称号を取得（新しい方法：ディスカッションアイテム内を探す）
                                    author_tier = self._get_author_tier_from_item(item, author)
                                    if author_tier:
                                        print(f"    [{idx}] {author}: {author_tier}")

                                    # 称号色を取得
                                    tier_color = self._get_tier_color_from_item(item)
                                    if tier_color:
                                        print(f"    [{idx}] Tier color: {tier_color}")
                                    break

                            # 投票数
                            vote_count = 0
                            vote_locator = item.locator('span[aria-label*="vote"]').first
                            if vote_locator.count() > 0:
                                vote_label = vote_locator.get_attribute('aria-label')
                                if vote_label:
                                    try:
                                        vote_count = int(vote_label.split()[0])
                                    except (ValueError, IndexError):
                                        pass

                            # コメント数
                            comment_count = 0
                            comment_locators = item.locator('span').all()
                            for comment_loc in comment_locators:
                                text = comment_loc.text_content()
                                if text and 'comment' in text.lower():
                                    try:
                                        comment_count = int(text.split()[0])
                                        break
                                    except (ValueError, IndexError):
                                        pass

                            # ピン留めチェック - ピン留めは除外
                            is_pinned = item.locator('text=push_pin').count() > 0
                            if is_pinned:
                                continue  # Pinned topicsはスキップ

                            all_discussions.append({
                                'title': title,
                                'url': discussion_url,
                                'author': author,
                                'author_tier': author_tier,
                                'tier_color': tier_color,
                                'vote_count': vote_count,
                                'comment_count': comment_count,
                                'category': None,
                                'is_pinned': False,  # ピン留めは除外しているので常にFalse
                            })

                        except Exception as e:
                            print(f"    ディスカッションアイテム解析エラー [{idx}]: {e}")
                            continue

                browser.close()

                print(f"\n取得完了: {len(all_discussions)}件")

                # 投票数でソート（Kaggleのページと同じ順序を維持）
                sorted_discussions = sorted(all_discussions, key=lambda x: x['vote_count'], reverse=True)

                # キャッシュに保存
                if sorted_discussions:
                    result = {
                        'comp_id': comp_id,
                        'max_pages': max_pages,
                        'scraped_at': datetime.now().isoformat(),
                        'discussions': sorted_discussions
                    }
                    self.cache_service.set_scraped_data(
                        cache_key,
                        result,
                        ttl_days=self.cache_ttl_days
                    )

                print(f"✓ {len(sorted_discussions)}件のディスカッションを保存しました")
                return sorted_discussions

        except Exception as e:
            print(f"✗ スクレイピング失敗 ({comp_id} discussions): {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_discussion_detail(
        self,
        discussion_url: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        個別ディスカッションの詳細を取得

        Args:
            discussion_url: ディスカッションのURL
            force_refresh: キャッシュを無視して再取得

        Returns:
            ディスカッション詳細の辞書（取得失敗時は None）
        """
        # キャッシュキー（URLの最後の部分を使用）
        discussion_id = discussion_url.split('/')[-1].split('#')[0]
        cache_key = f"discussion:{discussion_id}"

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                print(f"✓ キャッシュから取得: {discussion_id}")
                return cached_data

        print(f"🌐 ディスカッション詳細スクレイピング: {discussion_id}")

        try:
            with sync_playwright() as p:
                browser: Browser = p.chromium.launch(headless=self.headless)
                page: Page = browser.new_page()

                # ページに移動
                response = page.goto(discussion_url, wait_until="networkidle", timeout=30000)

                # 404チェック
                if response and response.status == 404:
                    print(f"❌ ディスカッションが見つかりません: {discussion_url}")
                    browser.close()
                    return None

                # JavaScriptレンダリング完了を待機
                page.wait_for_load_state('networkidle')
                time.sleep(2)

                # メインコンテンツを取得
                content_text = page.inner_text('#site-content')
                browser.close()

                # 結果を作成
                result = {
                    'discussion_id': discussion_id,
                    'url': discussion_url,
                    'scraped_at': datetime.now().isoformat(),
                    'content': content_text,
                }

                # キャッシュに保存
                self.cache_service.set_scraped_data(
                    cache_key,
                    result,
                    ttl_days=self.cache_ttl_days
                )

                print(f"✓ 取得完了: {discussion_id} ({len(content_text)} 文字)")
                return result

        except Exception as e:
            print(f"✗ ディスカッション詳細スクレイピング失敗 ({discussion_id}): {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_multiple(
        self,
        comp_ids: list[str],
        delay_seconds: float = 2.0
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        複数のコンペティションをスクレイピング（レート制限対応）

        Args:
            comp_ids: コンペティション ID のリスト
            delay_seconds: リクエスト間の待機時間（秒）

        Returns:
            {comp_id: scraped_data} の辞書
        """
        results = {}

        for i, comp_id in enumerate(comp_ids):
            print(f"\n[{i+1}/{len(comp_ids)}] 処理中: {comp_id}")

            # スクレイピング実行
            data = self.get_competition_details(comp_id)
            results[comp_id] = data

            # レート制限対策（最後の1件以外）
            if i < len(comp_ids) - 1:
                print(f"⏳ {delay_seconds}秒待機...")
                time.sleep(delay_seconds)

        return results


# グローバルインスタンス（シングルトンパターン）
_scraper_service_instance = None


def get_scraper_service(cache_ttl_days: int = 1) -> ScraperService:
    """スクレイピングサービスのインスタンスを取得（シングルトン）"""
    global _scraper_service_instance
    if _scraper_service_instance is None:
        _scraper_service_instance = ScraperService(cache_ttl_days=cache_ttl_days)
    return _scraper_service_instance
