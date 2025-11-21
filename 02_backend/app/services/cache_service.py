"""
キャッシュサービス

スクレイピング結果を一時保存して、重複スクレイピングを防ぐ
"""

import json
from typing import Optional
import redis
from datetime import datetime


class CacheService:
    """Redis を使ったキャッシュサービス"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        初期化

        Args:
            host: Redis ホスト
            port: Redis ポート
            db: Redis データベース番号
        """
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True  # 文字列として取得
            )
            # 接続テスト
            self.redis.ping()
            print(f"✅ Redis 接続成功: {host}:{port}")
        except redis.ConnectionError as e:
            print(f"❌ Redis 接続失敗: {e}")
            print("⚠️  キャッシュなしで動作します")
            self.redis = None

    def get_scraped_data(self, comp_id: str) -> Optional[dict]:
        """
        キャッシュからスクレイピングデータを取得

        Args:
            comp_id: コンペティション ID

        Returns:
            キャッシュデータ（なければ None）
        """
        if not self.redis:
            return None

        try:
            key = f"scraped:{comp_id}"
            data = self.redis.get(key)

            if data:
                print(f"📦 キャッシュヒット: {comp_id}")
                return json.loads(data)
            else:
                print(f"⏭️  キャッシュミス: {comp_id}")
                return None

        except Exception as e:
            print(f"❌ キャッシュ取得エラー ({comp_id}): {e}")
            return None

    def set_scraped_data(
        self,
        comp_id: str,
        data: dict,
        ttl_days: int = 1
    ) -> bool:
        """
        スクレイピングデータをキャッシュに保存

        Args:
            comp_id: コンペティション ID
            data: スクレイピングデータ
            ttl_days: 有効期限（日数）

        Returns:
            成功したか
        """
        if not self.redis:
            return False

        try:
            key = f"scraped:{comp_id}"
            ttl_seconds = ttl_days * 24 * 60 * 60

            # データにメタ情報を追加
            cache_data = {
                **data,
                "cached_at": datetime.now().isoformat()
            }

            # 保存
            self.redis.setex(
                key,
                ttl_seconds,
                json.dumps(cache_data, ensure_ascii=False)
            )

            print(f"💾 キャッシュ保存: {comp_id} (TTL: {ttl_days}日)")
            return True

        except Exception as e:
            print(f"❌ キャッシュ保存エラー ({comp_id}): {e}")
            return False

    def delete_cache(self, comp_id: str) -> bool:
        """
        特定のコンペのキャッシュを削除

        Args:
            comp_id: コンペティション ID

        Returns:
            成功したか
        """
        if not self.redis:
            return False

        try:
            key = f"scraped:{comp_id}"
            result = self.redis.delete(key)

            if result:
                print(f"🗑️  キャッシュ削除: {comp_id}")
            return bool(result)

        except Exception as e:
            print(f"❌ キャッシュ削除エラー ({comp_id}): {e}")
            return False

    def clear_all_cache(self) -> bool:
        """
        すべてのキャッシュを削除

        Returns:
            成功したか
        """
        if not self.redis:
            return False

        try:
            keys = self.redis.keys("scraped:*")
            if keys:
                self.redis.delete(*keys)
                print(f"🗑️  全キャッシュ削除: {len(keys)}件")
            else:
                print("⏭️  削除するキャッシュがありません")
            return True

        except Exception as e:
            print(f"❌ 全キャッシュ削除エラー: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """
        キャッシュの統計情報を取得

        Returns:
            統計情報
        """
        if not self.redis:
            return {"enabled": False}

        try:
            keys = self.redis.keys("scraped:*")
            return {
                "enabled": True,
                "total_cached": len(keys),
                "cached_competitions": [key.replace("scraped:", "") for key in keys[:10]]  # 最初の10件
            }
        except Exception as e:
            print(f"❌ 統計取得エラー: {e}")
            return {"enabled": False, "error": str(e)}

    # ============================================
    # ディスカッション・解法のコンテンツキャッシュ
    # （容量削減のため、DBではなくRedisに3日間保存）
    # ============================================

    CONTENT_TTL_DAYS = 3  # 3日間

    def save_discussion_content(self, discussion_id: int, content: str) -> bool:
        """
        ディスカッションのコンテンツをキャッシュに保存（3日間）

        Args:
            discussion_id: ディスカッションID
            content: コンテンツ（HTML）

        Returns:
            保存成功したかどうか
        """
        if not self.redis:
            return False

        try:
            key = f"discussion:{discussion_id}:content"
            ttl_seconds = self.CONTENT_TTL_DAYS * 24 * 60 * 60
            self.redis.setex(key, ttl_seconds, content)
            print(f"💾 ディスカッションコンテンツ保存: {discussion_id} (TTL: {self.CONTENT_TTL_DAYS}日)")
            return True
        except Exception as e:
            print(f"❌ ディスカッションコンテンツ保存エラー ({discussion_id}): {e}")
            return False

    def get_discussion_content(self, discussion_id: int) -> Optional[str]:
        """
        ディスカッションのコンテンツをキャッシュから取得

        Args:
            discussion_id: ディスカッションID

        Returns:
            コンテンツ（HTML）、存在しない場合はNone
        """
        if not self.redis:
            return None

        try:
            key = f"discussion:{discussion_id}:content"
            content = self.redis.get(key)
            if content:
                print(f"📦 ディスカッションコンテンツキャッシュヒット: {discussion_id}")
            return content
        except Exception as e:
            print(f"❌ ディスカッションコンテンツ取得エラー ({discussion_id}): {e}")
            return None

    def save_solution_content(self, solution_id: int, content: str) -> bool:
        """
        解法のコンテンツをキャッシュに保存（3日間）

        Args:
            solution_id: 解法ID
            content: コンテンツ（HTML）

        Returns:
            保存成功したかどうか
        """
        if not self.redis:
            return False

        try:
            key = f"solution:{solution_id}:content"
            ttl_seconds = self.CONTENT_TTL_DAYS * 24 * 60 * 60
            self.redis.setex(key, ttl_seconds, content)
            print(f"💾 解法コンテンツ保存: {solution_id} (TTL: {self.CONTENT_TTL_DAYS}日)")
            return True
        except Exception as e:
            print(f"❌ 解法コンテンツ保存エラー ({solution_id}): {e}")
            return False

    def get_solution_content(self, solution_id: int) -> Optional[str]:
        """
        解法のコンテンツをキャッシュから取得

        Args:
            solution_id: 解法ID

        Returns:
            コンテンツ（HTML）、存在しない場合はNone
        """
        if not self.redis:
            return None

        try:
            key = f"solution:{solution_id}:content"
            content = self.redis.get(key)
            if content:
                print(f"📦 解法コンテンツキャッシュヒット: {solution_id}")
            return content
        except Exception as e:
            print(f"❌ 解法コンテンツ取得エラー ({solution_id}): {e}")
            return None

    def get_content_ttl(self, discussion_id: Optional[int] = None, solution_id: Optional[int] = None) -> Optional[int]:
        """
        コンテンツキャッシュの残り有効期限を取得（秒）

        Args:
            discussion_id: ディスカッションID（オプション）
            solution_id: 解法ID（オプション）

        Returns:
            残り秒数、キーが存在しない場合はNone
        """
        if not self.redis:
            return None

        try:
            if discussion_id is not None:
                key = f"discussion:{discussion_id}:content"
            elif solution_id is not None:
                key = f"solution:{solution_id}:content"
            else:
                return None

            ttl = self.redis.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            print(f"❌ TTL取得エラー: {e}")
            return None


# グローバルインスタンス（シングルトンパターン）
_cache_service_instance = None


def get_cache_service() -> CacheService:
    """キャッシュサービスのインスタンスを取得（シングルトン）"""
    global _cache_service_instance
    if _cache_service_instance is None:
        _cache_service_instance = CacheService()
    return _cache_service_instance
