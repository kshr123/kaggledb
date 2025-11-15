# 20. Webスクレイピング機能の実装（2025-11-16）

## 📋 概要

Kaggle APIでは取得できない詳細情報を、Webスクレイピングで取得する機能を実装しました。

---

## 🎯 実装した機能

### 1. Redis キャッシュシステム

**目的**: 重複スクレイピングを防止し、Kaggle サーバーへの負荷を軽減

**実装内容**:
- **Redis 8.2.3** のインストールと起動
- **Python redis パッケージ** の導入
- **キャッシュサービス** (`02_backend/app/services/cache_service.py`)

**主な機能**:
```python
class CacheService:
    def get_scraped_data(comp_id: str) -> Optional[dict]
    def set_scraped_data(comp_id: str, data: dict, ttl_days: int = 1) -> bool
    def delete_cache(comp_id: str) -> bool
    def clear_all_cache() -> bool
    def get_cache_stats() -> dict
```

**特徴**:
- **Graceful Degradation**: Redis が利用できない場合でも動作
- **TTL**: デフォルト 1 日間（最大 3 日まで設定可能）
- **Singleton パターン**: グローバルインスタンスで効率的に管理

---

### 2. Playwright Webスクレイピング

**課題**: Kaggle のページは React SPA で JavaScript レンダリングされるため、通常の `requests` では空の HTML しか取得できない

**解決策**: Playwright Python ライブラリを使用して、JavaScript レンダリング後のコンテンツを取得

**実装内容**:
- **Playwright** のインストール（Chromium ブラウザ含む）
- **スクレイピングサービス** (`02_backend/app/services/scraper_service.py`)

**主な機能**:
```python
class ScraperService:
    def get_competition_details(comp_id: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]
    def scrape_multiple(comp_ids: list[str], delay_seconds: float = 2.0) -> Dict[str, Optional[Dict[str, Any]]]
```

**取得データ**:
```python
{
    'comp_id': 'titanic',
    'url': 'https://www.kaggle.com/competitions/titanic',
    'scraped_at': '2025-11-16T01:41:52.611276',
    'full_text': '...'  # LLM 処理用の全テキスト（約10,000文字）
}
```

**設計判断**:
- ❌ **HTML パーサーで細かく抽出しない**: セレクターのメンテナンスコストが高い
- ✅ **全テキストを取得して LLM で処理**: シンプルで柔軟性が高い

---

### 3. データベーススキーマ拡張

**追加カラム**: `last_scraped_at TIMESTAMP`

**目的**: 最後にスクレイピングした日時を記録し、再スクレイピングの判断に使用

**実装**:
1. `schema.sql` の更新
2. マイグレーションスクリプト (`04_scripts/add_last_scraped_at.py`)
3. 既存データベースへの適用完了

---

### 4. テスト・デバッグスクリプト

#### `04_scripts/test_scraping.py`
スクレイピング機能の動作確認

```bash
python test_scraping.py
```

**テスト結果**:
- ✅ titanic: 9,927 文字
- ❌ house-prices: 404エラー（URL異なる）
- ✅ digit-recognizer: 8,624 文字

#### `04_scripts/test_playwright_scraping.py`
Playwright で HTML を取得して保存

#### `04_scripts/inspect_kaggle_page.py`
HTML 構造の調査用

---

## 🏗️ アーキテクチャ

### データフロー

```
1. Kaggle コンペティションページ
   ↓
2. Playwright でレンダリング（ヘッドレスブラウザ）
   ↓
3. ページ全体のテキスト抽出
   ↓
4. Redis キャッシュに保存（TTL: 1日）
   ↓
5. LLM で処理（要約・タグ生成・評価指標抽出）
   ↓
6. データベースに永続化
```

### キャッシュ戦略

**目的**: 重複スクレイピング防止（ユーザーへの情報提供ではない）

**設計判断**:
- ✅ **短期キャッシュ**: 1日（最大3日）
- ✅ **シンプル**: 全データ同じ TTL
- ❌ **長期保存しない**: ユーザーは Kaggle URL を直接見る

**ストレージ戦略**:
- **Redis**: スクレイピング結果の一時保存（raw data）
- **DB**: LLM 生成の要約・タグのみ永続化
- **Kaggle URL**: 詳細情報はユーザーが直接確認

---

## 🔧 技術的な課題と解決

### 課題 1: JavaScript レンダリング

**問題**: `requests` では空の HTML しか取得できない
```html
<div id="root"></div>  <!-- React が後からレンダリング -->
```

**解決**: Playwright でブラウザを起動し、レンダリング完了を待機
```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle')
    page.wait_for_load_state('networkidle')
    time.sleep(2)  # 追加の安全待機
    text = page.inner_text('#site-content')
```

### 課題 2: MCP vs ライブラリ直接使用

**議論**: MCP (Playwright) を使うべきか？

**結論**: ❌ MCP は使わず、**Playwright Python ライブラリを直接使用**

**理由**:
- MCP は自然言語での対話用
- プログラムでの自動化には直接ライブラリの方が効率的
- コードの可読性・保守性が向上

### 課題 3: データ抽出方法

**アプローチ A**: BeautifulSoup で細かく抽出
- ❌ セレクターのメンテナンスコスト
- ❌ Kaggle のデザイン変更に脆弱

**アプローチ B**: 全テキスト取得 + LLM 処理
- ✅ シンプル
- ✅ 柔軟性が高い
- ✅ メンテナンスコストが低い

**採用**: **アプローチ B**

---

## 📊 パフォーマンス

### スクレイピング時間
- 1コンペあたり約 10-15 秒
- レート制限対策: コンペ間で 2 秒待機

### キャッシュ効果
- 2回目のリクエストは即座に返る（Redis から取得）
- Kaggle サーバーへの負荷を大幅削減

---

## 🔄 今後の拡張

### Phase 2: 動的コンテンツ

現在は静的コンテンツのみ対応：
- コンペ説明
- 評価指標
- データセット情報

**将来対応予定**:
- ディスカッション（短い TTL）
- リーダーボード（短い TTL）
- 新着ノートブック

---

## 📝 残タスク

### 優先度: 高
- [ ] `enrich_competitions.py` をスクレイピング対応に更新
- [ ] スクレイピング結果を LLM で処理
- [ ] データベースへの保存ロジック実装

### 優先度: 中
- [ ] エラーハンドリングの強化
- [ ] ログ出力の改善
- [ ] パフォーマンスモニタリング

### 優先度: 低
- [ ] Phase 2 機能（ディスカッション等）

---

## 🔗 関連ファイル

### 新規作成
- `02_backend/app/services/cache_service.py` - Redis キャッシュサービス
- `02_backend/app/services/scraper_service.py` - Playwright スクレイピング
- `04_scripts/add_last_scraped_at.py` - DB マイグレーション
- `04_scripts/test_scraping.py` - テストスクリプト
- `04_scripts/test_playwright_scraping.py` - Playwright テスト
- `04_scripts/inspect_kaggle_page.py` - HTML 調査ツール

### 変更
- `02_backend/schema.sql` - `last_scraped_at` カラム追加

---

## 🎓 学習ポイント

### 1. MCP の適切な使い方
- **MCP**: 自然言語での対話・探索用
- **ライブラリ**: プログラムでの自動化用
- 適材適所で使い分ける

### 2. スクレイピングのベストプラクティス
- レート制限を守る（2秒待機）
- キャッシュで重複リクエストを防ぐ
- Graceful Degradation（Redis なしでも動作）

### 3. データ抽出戦略
- 細かいパースより LLM 処理の方がメンテナンスしやすい
- 柔軟性と保守性のバランス

---

**作成日**: 2025-11-16
**最終更新**: 2025-11-16
