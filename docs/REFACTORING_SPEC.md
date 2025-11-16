# バックエンドリファクタリング仕様書

## 目的

バックエンドコードを適切なコンポーネントに分割し、パフォーマンスと運用効率を向上させる。

## 現状の問題点

### 1. コードの肥大化
- `routers/competitions.py`: 859行（理想は200行以下）
- 複数の責務が混在（CRUD、スクレイピング、解法管理、要約生成）

### 2. アーキテクチャの課題
- **データアクセス層の欠如**: SQLが直接ルーターに書かれている
- **モデル定義の不在**: データ構造が暗黙的
- **ビジネスロジックの分散**: ルーターとサービスに散在

### 3. 保守性・テスタビリティの低下
- モック困難（DB操作が直書き）
- 単一責任の原則違反
- 拡張が困難

## 新アーキテクチャ

### レイヤー構造

```
┌─────────────────────────────────────┐
│  Routers (API Endpoints)            │  ← エンドポイント定義のみ
├─────────────────────────────────────┤
│  Services (Business Logic)          │  ← ビジネスロジック
├─────────────────────────────────────┤
│  Repositories (Data Access)         │  ← データアクセス抽象化
├─────────────────────────────────────┤
│  Models (Data Structures)           │  ← データ構造定義
├─────────────────────────────────────┤
│  Database                            │  ← SQLite
└─────────────────────────────────────┘
```

### ディレクトリ構造

```
02_backend/app/
├── models/                  # データモデル（新規）
│   ├── __init__.py
│   ├── competition.py      # Competition, CompetitionDetail
│   ├── discussion.py       # Discussion
│   ├── solution.py         # Solution
│   └── tag.py             # Tag
│
├── repositories/           # データアクセス層（新規）
│   ├── __init__.py
│   ├── base.py            # BaseRepository
│   ├── competition.py     # CompetitionRepository
│   ├── discussion.py      # DiscussionRepository
│   ├── solution.py        # SolutionRepository
│   └── tag.py            # TagRepository
│
├── services/              # ビジネスロジック層（拡張）
│   ├── __init__.py
│   ├── cache_service.py
│   ├── competition_service.py  # 新規: コンペ関連ビジネスロジック
│   ├── discussion_service.py   # 新規: ディスカッション管理
│   ├── solution_service.py     # 新規: 解法管理
│   ├── kaggle_client.py
│   ├── llm_service.py
│   └── scraper_service.py
│
├── routers/               # APIエンドポイント（簡潔化）
│   ├── __init__.py
│   ├── competitions.py    # リファクタ: 基本CRUD
│   ├── discussions.py     # 新規: ディスカッション操作
│   ├── solutions.py       # 新規: 解法操作
│   └── tags.py
│
├── database.py            # 新規: DB接続管理
├── config.py
└── main.py
```

## 各コンポーネントの責務

### Models（データモデル）
**責務**: データ構造の定義
```python
# models/competition.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Competition:
    id: str
    title: str
    url: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: str
    metric: Optional[str]
    description: Optional[str]
    # ...
```

### Repositories（データアクセス層）
**責務**: データベース操作の抽象化
```python
# repositories/competition.py
class CompetitionRepository(BaseRepository):
    def get_by_id(self, comp_id: str) -> Optional[Competition]:
        """IDでコンペを取得"""

    def list(self, limit: int, offset: int, filters: dict) -> List[Competition]:
        """コンペ一覧を取得"""

    def create(self, competition: Competition) -> Competition:
        """コンペを作成"""

    def update(self, competition: Competition) -> Competition:
        """コンペを更新"""
```

### Services（ビジネスロジック層）
**責務**: ビジネスルールの実装
```python
# services/competition_service.py
class CompetitionService:
    def __init__(
        self,
        repo: CompetitionRepository,
        scraper: ScraperService,
        llm: LLMService
    ):
        self.repo = repo
        self.scraper = scraper
        self.llm = llm

    def enrich_competition(self, comp_id: str) -> Competition:
        """コンペ情報を充実化（スクレイピング+LLM要約）"""
        comp = self.repo.get_by_id(comp_id)
        overview = self.scraper.get_tab_content(comp_id, "")
        data_info = self.scraper.get_tab_content(comp_id, "data")
        enriched = self.llm.enrich_competition(comp, overview, data_info)
        return self.repo.update(enriched)
```

### Routers（APIエンドポイント）
**責務**: HTTPリクエスト/レスポンスのハンドリングのみ
```python
# routers/competitions.py
@router.get("/{comp_id}")
def get_competition(comp_id: str):
    """コンペ詳細取得"""
    service = get_competition_service()
    comp = service.get_by_id(comp_id)
    if not comp:
        raise HTTPException(404, "Competition not found")
    return comp
```

## パフォーマンス最適化

### 1. データベース接続プーリング
```python
# database.py
from contextlib import contextmanager

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None

    @contextmanager
    def get_connection(self):
        """コネクションプーリング"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
```

### 2. リポジトリレベルでのキャッシング
```python
class CompetitionRepository(BaseRepository):
    def __init__(self, db: Database, cache: CacheService):
        self.db = db
        self.cache = cache

    def get_by_id(self, comp_id: str) -> Optional[Competition]:
        # キャッシュチェック
        cached = self.cache.get(f"comp:{comp_id}")
        if cached:
            return cached

        # DB取得
        comp = self._fetch_from_db(comp_id)

        # キャッシュ保存
        if comp:
            self.cache.set(f"comp:{comp_id}", comp, ttl=3600)

        return comp
```

### 3. バッチ操作の最適化
```python
class CompetitionRepository(BaseRepository):
    def bulk_create(self, competitions: List[Competition]) -> int:
        """一括挿入（トランザクション使用）"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO competitions (...) VALUES (...)",
                [(c.id, c.title, ...) for c in competitions]
            )
            conn.commit()
            return len(competitions)
```

## テスト戦略

### 1. ユニットテスト
- **Models**: データクラスのバリデーション
- **Repositories**: モックDBを使用したCRUD操作
- **Services**: モックリポジトリを使用したビジネスロジック

### 2. 統合テスト
- **Routers**: 実際のDBを使用したエンドツーエンドテスト

### 3. テストカバレッジ目標
- 全体: 80%以上
- ビジネスロジック（Services）: 90%以上

## 移行戦略

### Phase 1: 基盤構築
1. Models作成
2. Database接続管理作成
3. BaseRepository作成

### Phase 2: Repository層実装
1. CompetitionRepository
2. DiscussionRepository
3. SolutionRepository
4. TagRepository

### Phase 3: Service層実装
1. CompetitionService
2. DiscussionService
3. SolutionService

### Phase 4: Router層リファクタリング
1. competitions.py簡潔化
2. discussions.py分離
3. solutions.py分離

### Phase 5: テスト・検証
1. 全テスト実行
2. パフォーマンステスト
3. ドキュメント更新

## 成功基準

### 機能要件
- ✅ 既存の全APIエンドポイントが動作
- ✅ レスポンスタイムが劣化しない
- ✅ 全テストがパス

### 非機能要件
- ✅ コードの平均複雑度が20以下
- ✅ 各ファイルが300行以下
- ✅ テストカバレッジ80%以上

### 保守性
- ✅ 新機能追加が容易
- ✅ バグ修正の影響範囲が明確
- ✅ コードレビューが効率的

## リスクと対策

### リスク1: 既存機能の破壊
**対策**:
- 全テストを事前に整備
- 段階的な移行（フィーチャーフラグ使用）

### リスク2: パフォーマンス劣化
**対策**:
- ベンチマークテストを実施
- キャッシング戦略を最適化

### リスク3: 移行期間の長期化
**対策**:
- 小さな単位で段階的に移行
- 各フェーズで動作確認

## スケジュール

- **Phase 1-2**: 1-2時間（基盤+Repository）
- **Phase 3**: 1時間（Service層）
- **Phase 4**: 1時間（Router層）
- **Phase 5**: 30分（テスト・検証）

**合計**: 約4-5時間
