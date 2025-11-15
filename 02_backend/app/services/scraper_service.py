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
