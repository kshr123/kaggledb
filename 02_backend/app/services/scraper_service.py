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
        コンペティションのディスカッション一覧を取得（Discussions + Writeups の両方）

        Kaggleは自動的に投票数順にソートされているため、
        1ページ目を取得すれば最も重要なディスカッションが得られる

        Args:
            comp_id: コンペティション ID
            max_pages: 取得する最大ページ数（デフォルト1ページ）
            force_refresh: キャッシュを無視して再取得

        Returns:
            ディスカッション情報のリスト（Discussions + Writeups）
        """
        # キャッシュキー
        cache_key = f"{comp_id}:discussions:p{max_pages}"

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                print(f"✓ キャッシュから取得: {comp_id} discussions")
                return cached_data.get('discussions', cached_data)

        base_url = f"{self.base_url}/{comp_id}/discussion?sort=votes"

        # Discussions タブと Writeups タブの両方を取得
        tabs = [
            ('discussion', base_url),
            ('writeup', f"{base_url}&tab=writeups")
        ]

        try:
            with sync_playwright() as p:
                browser: Browser = p.chromium.launch(headless=self.headless)
                page: Page = browser.new_page()

                all_discussions = []
                seen_urls = set()  # 重複チェック用

                # 各タブをスクレイピング
                for tab_type, tab_url in tabs:
                    print(f"\n📋 {tab_type.upper()} タブをスクレイピング中...")

                    for page_num in range(1, max_pages + 1):
                        page_url = f"{tab_url}&page={page_num}" if page_num > 1 else tab_url

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
                                # タイトルとURL（/discussion/ または /writeups/ の両方に対応）
                                title_link = item.locator('a[href*="/competitions/"]').first
                                if title_link.count() == 0:
                                    continue

                                raw_title = title_link.text_content(timeout=3000).strip()
                                href = title_link.get_attribute('href')
                                discussion_url = f"https://www.kaggle.com{href}" if href.startswith('/') else href

                                # URLから category を判定
                                category = 'writeup' if '/writeups/' in discussion_url else 'discussion'

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
                                    continue  # Pinned topicsはスキップ（ユーザー要望）

                                # タイトルのクリーニング
                                # パターン: "[Title][Author] · Last comment..." or "[Title][Author]"
                                title = raw_title

                                # " · Last comment..." 以降を削除
                                if ' · Last comment' in title:
                                    title = title.split(' · Last comment')[0]

                                # 末尾の作者名を削除（作者名が取得できている場合）
                                if author and title.endswith(author):
                                    title = title[:-len(author)].strip()

                                # その他のクリーニング（念のため）
                                title = title.strip()

                                # 重複チェック: URLが既に追加済みの場合はスキップ
                                if discussion_url in seen_urls:
                                    continue

                                seen_urls.add(discussion_url)
                                all_discussions.append({
                                    'title': title,
                                    'url': discussion_url,
                                    'author': author,
                                    'author_tier': author_tier,
                                    'tier_color': tier_color,
                                    'vote_count': vote_count,
                                    'comment_count': comment_count,
                                    'category': category,  # URLから判定した category を設定
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

    def get_notebooks(
        self,
        comp_id: str,
        max_pages: int = 1,
        force_refresh: bool = False
    ) -> Optional[list[Dict[str, Any]]]:
        """
        コンペティションのノートブック一覧を取得（Codeタブ）

        Args:
            comp_id: コンペティション ID
            max_pages: 取得する最大ページ数（デフォルト1ページ）
            force_refresh: キャッシュを無視して再取得

        Returns:
            ノートブック情報のリスト
        """
        # キャッシュキー
        cache_key = f"{comp_id}:notebooks:p{max_pages}"

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                print(f"✓ キャッシュから取得: {comp_id} notebooks")
                return cached_data.get('notebooks', cached_data)

        base_url = f"{self.base_url}/{comp_id}/code?sortBy=voteCount"

        try:
            with sync_playwright() as p:
                browser: Browser = p.chromium.launch(headless=self.headless)
                page: Page = browser.new_page()

                all_notebooks = []
                seen_urls = set()  # 重複チェック用

                print(f"\n📔 CODE タブをスクレイピング中...")

                for page_num in range(1, max_pages + 1):
                    page_url = f"{base_url}&page={page_num}" if page_num > 1 else base_url

                    page.goto(page_url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(2000)

                    # ノートブックアイテムを探す（実際のHTML構造に合わせる）
                    # 'km-listitem--large' クラスを持つdiv要素
                    notebook_items = page.locator('div.km-listitem--large').all()

                    if not notebook_items:
                        print(f"  ページ{page_num}: ノートブックが見つかりません")
                        break

                    print(f"  ページ{page_num}: {len(notebook_items)}件のノートブックを処理中...")

                    for idx, item in enumerate(notebook_items, 1):
                        try:
                            # タイトルを取得（aria-label属性から）
                            title_link = item.locator('a[aria-label][role="link"]').first
                            if title_link.count() == 0:
                                continue

                            title = title_link.get_attribute('aria-label')
                            if not title:
                                continue

                            # URLをコメントリンクから構築
                            comment_link = item.locator('a[href*="/comments"]').first
                            if comment_link.count() == 0:
                                continue

                            href = comment_link.get_attribute('href')
                            if not href:
                                continue

                            # /code/username/notebook-name/comments → /code/username/notebook-name
                            notebook_url = href.replace('/comments', '')
                            notebook_url = f"https://www.kaggle.com{notebook_url}" if notebook_url.startswith('/') else notebook_url

                            # 重複チェック
                            if notebook_url in seen_urls:
                                continue

                            seen_urls.add(notebook_url)

                            # 投稿者情報
                            author = None
                            author_tier = None
                            tier_color = None

                            # 作成者リンク: aria-label に "profile" を含む
                            author_links = item.locator('a[aria-label*="profile"]').all()
                            for author_link in author_links:
                                aria_label = author_link.get_attribute('aria-label')
                                if aria_label and "'s profile" in aria_label:
                                    author = aria_label.split("'s profile")[0]
                                    print(f"    [{idx}] Author: {author}")

                                    # 称号を取得（TierバッジのテキストまたはSVG色から）
                                    # "Gold", "Silver", "Bronze" などのテキストを探す
                                    tier_spans = item.locator('span:has-text("Gold"), span:has-text("Silver"), span:has-text("Bronze"), span:has-text("Expert"), span:has-text("Master"), span:has-text("Grandmaster")').all()
                                    for tier_span in tier_spans:
                                        tier_text = tier_span.text_content().strip()
                                        if tier_text:
                                            author_tier = tier_text
                                            print(f"    [{idx}] {author}: {author_tier}")
                                            break

                                    # 称号色を取得
                                    tier_color = self._get_tier_color_from_item(item)
                                    if tier_color:
                                        print(f"    [{idx}] Tier color: {tier_color}")
                                    break

                            # 投票数（aria-label="N votes"）
                            vote_count = 0
                            vote_locator = item.locator('span[aria-label*="vote"]').first
                            if vote_locator.count() > 0:
                                vote_label = vote_locator.get_attribute('aria-label')
                                if vote_label:
                                    try:
                                        # "1246 votes" → 1246
                                        vote_count = int(vote_label.split()[0])
                                    except (ValueError, IndexError):
                                        pass

                            # コメント数（"89 comments"のようなテキスト）
                            comment_count = 0
                            if comment_link.count() > 0:
                                comment_text = comment_link.text_content()
                                if comment_text and 'comment' in comment_text.lower():
                                    try:
                                        # "89 comments" → 89
                                        comment_count = int(comment_text.split()[0])
                                    except (ValueError, IndexError):
                                        pass

                            all_notebooks.append({
                                'title': title,
                                'url': notebook_url,
                                'author': author,
                                'author_tier': author_tier,
                                'tier_color': tier_color,
                                'vote_count': vote_count,
                                'comment_count': comment_count,
                                'type': 'notebook'
                            })

                            print(f"    [{idx}] ✓ {title[:50]}... (votes={vote_count}, comments={comment_count})")

                        except Exception as e:
                            print(f"    ノートブックアイテム解析エラー [{idx}]: {e}")
                            continue

                browser.close()

                print(f"\n取得完了: {len(all_notebooks)}件")

                # 投票数でソート
                sorted_notebooks = sorted(all_notebooks, key=lambda x: x['vote_count'], reverse=True)

                # キャッシュに保存
                if sorted_notebooks:
                    result = {
                        'comp_id': comp_id,
                        'max_pages': max_pages,
                        'scraped_at': datetime.now().isoformat(),
                        'notebooks': sorted_notebooks
                    }
                    self.cache_service.set_scraped_data(
                        cache_key,
                        result,
                        ttl_days=self.cache_ttl_days
                    )

                print(f"✓ {len(sorted_notebooks)}件のノートブックを保存しました")
                return sorted_notebooks

        except Exception as e:
            print(f"✗ スクレイピング失敗 ({comp_id} notebooks): {e}")
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

    def get_writeups(
        self,
        comp_id: str,
        max_pages: int = 3,
        force_refresh: bool = False
    ) -> Optional[list[Dict[str, Any]]]:
        """
        コンペティションのWriteups（公式解法投稿）一覧を取得

        Args:
            comp_id: コンペティション ID
            max_pages: 取得する最大ページ数（デフォルト3ページ）
            force_refresh: キャッシュを無視して再取得

        Returns:
            Writeups情報のリスト
        """
        # キャッシュキー
        cache_key = f"{comp_id}:writeups:p{max_pages}"

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                print(f"✓ キャッシュから取得: {comp_id} writeups")
                return cached_data.get('writeups', cached_data)

        url = f"{self.base_url}/{comp_id}/writeups"
        print(f"スクレイピング: {url}")

        try:
            with sync_playwright() as p:
                browser: Browser = p.chromium.launch(headless=self.headless)
                page: Page = browser.new_page()

                all_writeups = []

                for page_num in range(1, max_pages + 1):
                    page_url = f"{url}?page={page_num}" if page_num > 1 else url

                    response = page.goto(page_url, wait_until="networkidle", timeout=30000)

                    # 404チェック（Writeupsページがない場合）
                    if response and response.status == 404:
                        print(f"  Writeupsページが見つかりません（コンペが古い可能性）")
                        break

                    page.wait_for_timeout(2000)

                    # Playwrightのlocator APIを使用（Discussionsと同じ構造）
                    writeup_items = page.locator('li.MuiListItem-root').all()

                    if not writeup_items:
                        print(f"  ページ{page_num}: Writeupsが見つかりません")
                        break

                    print(f"  ページ{page_num}: {len(writeup_items)}件のWriteupsを処理中...")

                    for idx, item in enumerate(writeup_items, 1):
                        try:
                            # タイトルとURL（/writeups/ を含むリンク）
                            title_link = item.locator('a[href*="/writeups/"]').first
                            if title_link.count() == 0:
                                continue

                            raw_title = title_link.text_content(timeout=3000).strip()
                            href = title_link.get_attribute('href')
                            writeup_url = f"https://www.kaggle.com{href}" if href.startswith('/') else href

                            # 投稿者情報
                            author = None
                            author_tier = None
                            tier_color = None
                            author_links = item.locator('a[aria-label*="profile"]').all()

                            for author_link in author_links:
                                aria_label = author_link.get_attribute('aria-label')
                                if aria_label and "'s profile" in aria_label:
                                    author = aria_label.split("'s profile")[0]
                                    print(f"    [{idx}] Author: {author}")

                                    # 称号を取得
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

                            # タイトルのクリーニング
                            title = raw_title
                            if ' · Last comment' in title:
                                title = title.split(' · Last comment')[0]
                            if author and title.endswith(author):
                                title = title[:-len(author)].strip()
                            title = title.strip()

                            all_writeups.append({
                                'title': title,
                                'url': writeup_url,
                                'author': author,
                                'author_tier': author_tier,
                                'tier_color': tier_color,
                                'vote_count': vote_count,
                                'comment_count': comment_count,
                                'category': 'writeup',
                                'is_pinned': False,
                            })

                        except Exception as e:
                            print(f"    Writeupアイテム解析エラー [{idx}]: {e}")
                            continue

                browser.close()

                print(f"\n取得完了: {len(all_writeups)}件")

                # 投票数でソート
                sorted_writeups = sorted(all_writeups, key=lambda x: x['vote_count'], reverse=True)

                # キャッシュに保存
                if sorted_writeups:
                    result = {
                        'comp_id': comp_id,
                        'max_pages': max_pages,
                        'scraped_at': datetime.now().isoformat(),
                        'writeups': sorted_writeups
                    }
                    self.cache_service.set_scraped_data(
                        cache_key,
                        result,
                        ttl_days=self.cache_ttl_days
                    )

                print(f"✓ {len(sorted_writeups)}件のWriteupsを保存しました")
                return sorted_writeups

        except Exception as e:
            print(f"✗ Writeupsスクレイピング失敗 ({comp_id}): {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_competition_metadata(
        self,
        comp_id: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        コンペページから構造化メタデータを取得

        Args:
            comp_id: コンペティションID
            force_refresh: キャッシュを無視して再取得

        Returns:
            メタデータ辞書（id, title, description, start_date, end_date, status, metric）
        """
        # キャッシュキー
        cache_key = f"comp_metadata:{comp_id}"

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                return cached_data

        url = f"{self.base_url}/{comp_id}"
        print(f"🌐 メタデータ取得: {comp_id}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()

                # ページに移動
                response = page.goto(url, wait_until='networkidle', timeout=30000)

                # 404チェック
                if response and response.status == 404:
                    print(f"❌ コンペが見つかりません: {comp_id}")
                    browser.close()
                    return None

                page.wait_for_load_state('networkidle')
                time.sleep(2)

                # HTMLを取得してパース
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                # 1. タイトル
                title = None
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text().strip()

                # 2. 説明文（最初の段落）
                description = None
                p_tags = soup.find_all('p')
                for p in p_tags:
                    text = p.get_text().strip()
                    if len(text) > 50:  # 十分な長さの段落を探す
                        description = text
                        break

                # 3. 全テキストから日付とステータスを抽出
                full_text = page.inner_text('body')
                lines = [line.strip() for line in full_text.split('\n')]

                start_date = None
                end_date = None
                status = None
                metric = None

                for line in lines:
                    line_lower = line.lower()

                    # 開始日
                    if not start_date and 'started' in line_lower:
                        # "Started 2 months ago" のような形式
                        start_date = line

                    # 終了日・ステータス
                    if not end_date:
                        if 'ended' in line_lower or 'closed' in line_lower:
                            end_date = line
                            status = 'completed'
                        elif 'closes' in line_lower or 'deadline' in line_lower:
                            end_date = line
                            status = 'active'

                    # 評価指標
                    if not metric and ('evaluation' in line_lower or 'metric' in line_lower):
                        # 次の行または同じ行から指標名を抽出
                        if len(line) < 100:  # 短い行なら指標の可能性
                            metric = line

                # ステータスが判定できない場合はendedから推測
                if not status:
                    if end_date and ('ended' in end_date.lower() or 'closed' in end_date.lower()):
                        status = 'completed'
                    else:
                        status = 'active'

                browser.close()

                # 結果を作成
                result = {
                    'id': comp_id,
                    'title': title,
                    'url': url,
                    'description': description,
                    'start_date': start_date,
                    'end_date': end_date,
                    'status': status,
                    'metric': metric,
                    'scraped_at': datetime.now().isoformat(),
                }

                # キャッシュに保存
                self.cache_service.set_scraped_data(
                    cache_key,
                    result,
                    ttl_days=self.cache_ttl_days
                )

                print(f"✓ {comp_id}: {title}")
                return result

        except Exception as e:
            print(f"❌ メタデータ取得エラー ({comp_id}): {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_competitions_list(
        self,
        max_pages: int = 10,
        prestige_filter: str = "medals",
        participation_filter: str = "open",
        force_refresh: bool = False,
        include_details: bool = False
    ) -> list[str] | list[Dict[str, Any]]:
        """
        Kaggleコンペ一覧ページからコンペIDのリストを取得

        Args:
            max_pages: 取得する最大ページ数
            prestige_filter: prestigeフィルター（"medals", "all"など）
            participation_filter: participationフィルター（"open", "all"など）
            force_refresh: キャッシュを無視して再取得
            include_details: タイトル・概要も含めて返すか

        Returns:
            include_details=False: コンペIDのリスト
            include_details=True: 詳細情報を含む辞書のリスト
        """
        # キャッシュキー
        cache_key = f"competitions_list:{prestige_filter}:{participation_filter}:p{max_pages}"
        if include_details:
            cache_key += ':details'

        # キャッシュチェック
        if not force_refresh:
            cached_data = self.cache_service.get_scraped_data(cache_key)
            if cached_data:
                if include_details:
                    comps = cached_data.get('competitions', [])
                    print(f"✓ キャッシュから取得: {len(comps)}件のコンペ詳細")
                    return comps
                else:
                    comp_ids = cached_data.get('competition_ids', [])
                    print(f"✓ キャッシュから取得: {len(comp_ids)}件のコンペID")
                    return comp_ids

        print(f"📍 コンペ一覧をスクレイピング中 (最大{max_pages}ページ)...")

        # include_detailsによって初期値を変える
        if include_details:
            all_comp_ids = []  # リスト
        else:
            all_comp_ids = set()  # セット

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()

                for page_num in range(1, max_pages + 1):
                    # URL構築
                    url = f"{self.base_url}?prestigeFilter={prestige_filter}&participationFilter={participation_filter}&page={page_num}"

                    try:
                        page.goto(url, wait_until='networkidle', timeout=60000)
                        time.sleep(2)

                        # スクロールしてコンテンツをロード
                        for i in range(3):
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            time.sleep(0.3)

                        # HTMLを取得してパース
                        html = page.content()
                        soup = BeautifulSoup(html, 'html.parser')

                        if include_details:
                            # 詳細情報付きで取得
                            # コンペカードを探す（各コンペは特定のdiv構造内にある）
                            comp_cards = soup.find_all('div', class_=lambda x: x and 'sc-kSaXSp' in str(x))

                            page_comps_detailed = []
                            for card in comp_cards:
                                # タイトル（最初のdivまたはspan）
                                title_elem = card.find('div', class_=lambda x: x and 'sc-kCuUfV' in str(x))
                                if not title_elem:
                                    title_elem = card.find('span', class_=lambda x: x and 'sc-kCuUfV' in str(x))

                                title = title_elem.get_text().strip() if title_elem else None

                                # 概要（説明文のspan）
                                desc_spans = card.find_all('span', class_=lambda x: x and 'sc-eqNDNG' in str(x) and 'sc-fYRIQK' in str(x))
                                description = None
                                for span in desc_spans:
                                    text = span.get_text().strip()
                                    # "Featured · Code Competition" のような行は除外
                                    if text and '·' not in text and len(text) > 20:
                                        description = text
                                        break

                                # コンペIDをリンクから取得
                                link = card.find_parent('a', href=lambda x: x and '/competitions/' in str(x))
                                if not link:
                                    # カード内のリンクを探す
                                    link = card.find('a', href=lambda x: x and '/competitions/' in str(x))

                                if link:
                                    href = link.get('href', '')
                                    comp_id = href.replace('/competitions/', '').split('/')[0].split('?')[0]

                                    if comp_id and title:
                                        page_comps_detailed.append({
                                            'id': comp_id,
                                            'title': title,
                                            'description': description or '',
                                            'url': f"https://www.kaggle.com/competitions/{comp_id}"
                                        })

                            all_comp_ids.extend(page_comps_detailed)
                            print(f"   ページ {page_num:2d}: {len(page_comps_detailed):2d}件 (合計: {len(all_comp_ids)}件)")

                            if len(page_comps_detailed) == 0:
                                print(f"   ページ {page_num} でデータなし、終了")
                                break
                        else:
                            # IDのみ取得（従来の方法）
                            comp_links = soup.find_all('a', href=lambda x: x and x.startswith('/competitions/') and x != '/competitions')
                            page_comps = set()
                            for link in comp_links:
                                href = link['href']
                                comp_id = href.replace('/competitions/', '').split('/')[0].split('?')[0]
                                if comp_id:
                                    page_comps.add(comp_id)

                            all_comp_ids.update(page_comps)
                            print(f"   ページ {page_num:2d}: {len(page_comps):2d}件 (合計: {len(all_comp_ids)}件)")

                            if len(page_comps) == 0:
                                print(f"   ページ {page_num} でデータなし、終了")
                                break

                    except Exception as e:
                        print(f"   ⚠️ ページ {page_num} のスクレイピングエラー: {e}")
                        break

                browser.close()

            if include_details:
                # 詳細情報付きリスト
                # 重複を除去（IDでユニーク化）
                seen_ids = set()
                unique_comps = []
                for comp in all_comp_ids:
                    if comp['id'] not in seen_ids:
                        seen_ids.add(comp['id'])
                        unique_comps.append(comp)

                # IDでソート
                unique_comps.sort(key=lambda x: x['id'])

                # キャッシュに保存
                if unique_comps:
                    result = {
                        'competitions': unique_comps,
                        'scraped_at': datetime.now().isoformat(),
                        'max_pages': max_pages,
                        'prestige_filter': prestige_filter,
                        'participation_filter': participation_filter,
                    }
                    self.cache_service.set_scraped_data(
                        cache_key,
                        result,
                        ttl_days=self.cache_ttl_days
                    )

                print(f"\n✅ 合計 {len(unique_comps)}件のコンペ詳細を取得しました")
                return unique_comps
            else:
                # IDのみのリスト
                comp_ids_list = sorted(list(all_comp_ids))

                # キャッシュに保存
                if comp_ids_list:
                    result = {
                        'competition_ids': comp_ids_list,
                        'scraped_at': datetime.now().isoformat(),
                        'max_pages': max_pages,
                        'prestige_filter': prestige_filter,
                        'participation_filter': participation_filter,
                    }
                    self.cache_service.set_scraped_data(
                        cache_key,
                        result,
                        ttl_days=self.cache_ttl_days
                    )

                print(f"\n✅ 合計 {len(comp_ids_list)}件のコンペIDを取得しました")
                return comp_ids_list

        except Exception as e:
            print(f"❌ コンペ一覧スクレイピングエラー: {e}")
            import traceback
            traceback.print_exc()
            return []

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
