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


# グローバルインスタンス（シングルトンパターン）
_cache_service_instance = None


def get_cache_service() -> CacheService:
    """キャッシュサービスのインスタンスを取得（シングルトン）"""
    global _cache_service_instance
    if _cache_service_instance is None:
        _cache_service_instance = CacheService()
    return _cache_service_instance
