# 16. キャッシュ戦略（Redis）

> **Phase 2以降**: Docker環境でRedisを導入し、画面更新を高速化

## 16.1 なぜRedisを使うのか？

### 問題: APIレスポンスが遅い
- **タグ一覧取得**: 60タグ × 6カテゴリ = 毎回DBクエリ
- **コンペ一覧**: ページングで毎回フルスキャン
- **統計情報**: 集計クエリは重い（COUNT, GROUP BY等）

### 解決: Redisキャッシュで高速化 ⚡
```
初回リクエスト: DB → Redis に保存 (例: 500ms)
2回目以降: Redis から返却 (例: 5ms) 🚀 100倍速い！
```

---

## 16.2 キャッシュ対象とTTL

| エンドポイント | キャッシュキー | TTL | 理由 |
|---------------|--------------|-----|------|
| `GET /api/tags` | `tags:all` | 1日 | タグは頻繁に変更されない |
| `GET /api/tags?group_by_category=true` | `tags:grouped` | 1日 | カテゴリ別タグも安定 |
| `GET /api/competitions?page=1&status=active` | `comps:page:1:active` | 1時間 | コンペ一覧は定期的に更新 |
| `GET /api/competitions/{id}` | `comp:{id}` | 6時間 | 詳細情報は比較的安定 |
| `GET /api/competitions/new` | `comps:new:30` | 1時間 | 新規コンペは日次で変化 |
| `GET /api/stats/summary` | `stats:summary` | 30分 | 統計は頻繁に更新不要 |

---

## 16.3 実装方針

### 16.3.1 キャッシュミドルウェア（デコレーター）

```python
from functools import wraps
import redis
import json

# Redisクライアント初期化
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def cache_response(key_prefix: str, ttl: int = 3600):
    """APIレスポンスをキャッシュするデコレーター"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # キャッシュキー生成（クエリパラメータを含む）
            cache_key = f"{key_prefix}:{hash(str(kwargs))}"

            # キャッシュから取得を試みる
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # キャッシュミス：DBから取得
            result = await func(*args, **kwargs)

            # Redisに保存
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator
```

### 16.3.2 使用例

```python
from app.cache import cache_response

@router.get("/tags")
@cache_response(key_prefix="tags:all", ttl=86400)  # 1日
def get_tags(category: Optional[str] = None):
    # DBクエリ（キャッシュヒット時はスキップされる）
    ...
    return tags

@router.get("/competitions")
@cache_response(key_prefix="comps:list", ttl=3600)  # 1時間
def get_competitions(page: int = 1, status: str = "all"):
    # ページネーションクエリ（キャッシュヒット時はスキップされる）
    ...
    return competitions
```

---

## 16.4 キャッシュ無効化（Invalidation）

### 手動無効化
新しいコンペを追加した時など、キャッシュをクリアする必要がある場合：

```python
@router.post("/competitions")
async def create_competition(competition: CompetitionCreate):
    # コンペを作成
    new_comp = create_competition_in_db(competition)

    # 関連キャッシュを無効化
    redis_client.delete("comps:*")  # コンペ関連のキャッシュをすべて削除
    redis_client.delete("stats:*")  # 統計キャッシュも削除

    return new_comp
```

### 自動無効化（TTL）
ほとんどのケースでは、TTL（Time To Live）による自動期限切れで十分。

---

## 16.5 画面更新が速くなる仕組み

### Before（Redis なし）⏳
```
ユーザー → フロントエンド → バックエンド → PostgreSQL
                                    ↓
                                 集計・JOIN
                                    ↓
                                 500-1000ms
```

### After（Redis あり）⚡
```
ユーザー → フロントエンド → バックエンド → Redis（キャッシュヒット）
                                    ↓
                                  5-10ms  🚀 50-100倍速い！
```

### 具体例: タグフィルタパネル

**シナリオ**: ホーム画面を開くたびに60タグを取得

- **Without Redis**:
  - SQLiteから60タグをSELECT → 50ms
  - ページを開くたびに50ms
  - 10回開く = 500ms

- **With Redis**:
  - 初回: SQLiteから60タグをSELECT → 50ms + Redis保存
  - 2回目以降: Redisから取得 → 5ms ⚡
  - 10回開く = 50ms + 9×5ms = 95ms（約5倍速い）

---

## 16.6 モニタリング

### Redis統計の確認
```bash
docker exec -it kaggledb-redis redis-cli INFO stats
```

**重要な指標**:
- `keyspace_hits`: キャッシュヒット数
- `keyspace_misses`: キャッシュミス数
- **ヒット率** = hits / (hits + misses)
  - 目標: 80%以上

### 開発環境でのテスト
```bash
# Redis接続確認
docker exec -it kaggledb-redis redis-cli PING
# → PONG

# キャッシュキーの確認
docker exec -it kaggledb-redis redis-cli KEYS '*'

# 特定キーの値を確認
docker exec -it kaggledb-redis redis-cli GET "tags:all"

# キャッシュをクリア（開発時）
docker exec -it kaggledb-redis redis-cli FLUSHALL
```

---

## 16.7 Phase 2 実装チェックリスト

- [ ] `requirements.txt` に `redis` パッケージを追加
- [ ] `app/cache.py` を作成（キャッシュデコレーター）
- [ ] `app/config.py` に Redis URL を追加
- [ ] 主要エンドポイントにキャッシュデコレーターを適用
  - [ ] `GET /api/tags`
  - [ ] `GET /api/competitions`
  - [ ] `GET /api/competitions/{id}`
  - [ ] `GET /api/stats/*`
- [ ] Docker Compose で Redis コンテナを起動
- [ ] キャッシュヒット率のモニタリング設定

---

**関連ドキュメント:**
- [技術スタック](./04_tech_stack.md)
- [Docker構成](./12_docker.md)
- [API設計](./07_api_design.md)
