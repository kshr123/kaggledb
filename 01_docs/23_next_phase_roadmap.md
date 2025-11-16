# 23. 次フェーズのロードマップ（2025-11-16）

## 📋 現在の実装状況

### ✅ 実装済み

| 項目 | 状態 | 備考 |
|------|------|------|
| **要約生成** | ✅ 実装済み | `summary` - LLM で構造化要約を生成 |
| **タグ生成** | ✅ 実装済み | `tags` - タスクタイプ、特徴等 |
| **データタイプ** | ✅ 実装済み | `data_types` - 画像、テキスト、テーブル等 |
| **ドメイン** | ✅ 実装済み | `domain` - 医療、金融、CV等 |
| **スクレイピング** | ✅ 実装済み | Playwright で詳細情報取得 |
| **キャッシュ** | ✅ 実装済み | Redis で重複スクレイピング防止 |

### ⚠️ 実装されているが未使用

| 項目 | 状態 | 問題点 |
|------|------|--------|
| **評価指標抽出** | ⚠️ 未使用 | `extract_evaluation_metric()` メソッドは存在するが、`enrich_competition()` で呼び出されていない |

### ❌ 未実装

| 項目 | 状態 | 優先度 |
|------|------|--------|
| **ディスカッション情報** | ❌ 未実装 | 🔴 高 |
| **データセット詳細** | ❌ 未実装 | 🟡 中 |
| **ノートブック情報** | ❌ 未実装 | 🟢 低 |
| **リーダーボード** | ❌ 未実装 | 🟢 低 |

---

## 🎯 Phase 1: 基本動作確認（今すぐ）

### Step 1: 実運用テスト（1-2件）
```bash
cd /Users/kotaro/Desktop/dev/kaggledb/02_backend
source .venv/bin/activate
python ../04_scripts/enrich_competitions.py --limit 2
```

**確認項目**:
- ✅ スクレイピング成功
- ✅ LLM 処理成功
- ✅ DB 更新成功（summary, tags, data_types, domain, last_scraped_at）
- ❌ **評価指標（metric）が更新されていない**

### Step 2: 一括処理テスト（5-10件）
```bash
python ../04_scripts/enrich_competitions.py --limit 10
```

**確認項目**:
- ✅ キャッシュ動作確認
- ✅ レート制限遵守
- ✅ エラーハンドリング

### Step 3: フロントエンド確認
```bash
# ブラウザで http://localhost:5173 を開く
```

**確認項目**:
- ✅ 要約が表示される
- ✅ タグが表示される
- ✅ データタイプが表示される
- ✅ ドメインが表示される
- ❌ **評価指標が表示されない可能性**

---

## 🎯 Phase 2: 欠落情報の補完（次のタスク）

### 2.1 評価指標（Metric）の抽出・保存

**現状の問題**:
- `extract_evaluation_metric()` メソッドは存在するが呼び出されていない
- DB の `metric` カラムが空のまま

**対応内容**:
1. `llm_service.py` の `enrich_competition()` を修正
2. 評価指標抽出を追加
3. DB 更新時に `metric` を保存

**実装例**:
```python
# llm_service.py の enrich_competition() 内
def enrich_competition(self, competition: Dict, available_tags: Optional[Dict[str, List[str]]] = None) -> Dict:
    # 既存: 要約生成
    if not competition.get("summary") and competition.get("description"):
        ...

    # 既存: タグ生成
    if (not competition.get("tags") or not competition.get("data_types")) and competition.get("description"):
        ...

    # 🆕 追加: 評価指標抽出
    if not competition.get("metric") and competition.get("description"):
        print(f"評価指標抽出中: {competition.get('title', 'Unknown')}")
        metric = self.extract_evaluation_metric(
            description=competition.get("description", ""),
            title=competition.get("title", "")
        )
        competition["metric"] = metric

    return competition
```

```python
# enrich_competitions.py の update_competition() 内
def update_competition(competition: Dict) -> bool:
    cursor.execute("""
        UPDATE competitions
        SET
            summary = ?,
            tags = ?,
            data_types = ?,
            domain = ?,
            metric = ?,           -- 🆕 追加
            last_scraped_at = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        competition.get("summary", ""),
        tags_json,
        data_types_json,
        competition.get("domain", ""),
        competition.get("metric", ""),  -- 🆕 追加
        competition.get("last_scraped_at"),
        now,
        competition["id"]
    ))
```

**テスト**:
```bash
# 1件で評価指標抽出テスト
python ../04_scripts/enrich_competitions.py --limit 1

# DB 確認
sqlite3 kaggle_competitions.db "SELECT id, title, metric FROM competitions WHERE metric IS NOT NULL AND metric != '' LIMIT 5;"
```

---

### 2.2 データセット情報の取得・整理

**現状の問題**:
- **Data タブ**（`/competitions/{id}/data`）は別ページ
- 現在は **Overview タブ**のみスクレイピング
- データセット詳細（ファイル一覧、サイズ、説明）は未取得

**Kaggle のタブ構造**:
```
/competitions/{id}           → Overview タブ（✅ 実装済み）
/competitions/{id}/data      → Data タブ（❌ 未実装）
/competitions/{id}/discussion → Discussion タブ（❌ 未実装）
/competitions/{id}/leaderboard → Leaderboard（⏸️ 保留）
/competitions/{id}/code      → Code/Notebooks（⏸️ 保留）
```

**実装内容**:

#### 2.2.1 Data タブのスクレイピング
```python
# scraper_service.py に追加
def get_data_tab(self, comp_id: str) -> Optional[Dict[str, Any]]:
    """
    Data タブから情報を取得

    Returns:
        {
            'comp_id': 'titanic',
            'url': 'https://www.kaggle.com/competitions/titanic/data',
            'scraped_at': '2025-11-16T...',
            'data_text': '...'  # Data タブのテキスト全体
        }
    """
    url = f"{self.base_url}/{comp_id}/data"
    # Playwright でスクレイピング（Overview と同じ実装）
    ...
```

#### 2.2.2 LLM でデータセット情報を抽出
```python
# llm_service.py に追加
def extract_dataset_info(self, data_text: str, title: str = "") -> Dict[str, Any]:
    """
    Data タブのテキストからデータセット情報を抽出

    Returns:
        {
            "files": ["train.csv", "test.csv", "sample_submission.csv"],
            "total_size": "1.2 GB",
            "description": "タイタニック乗客データ（891件の訓練データ）",
            "features": ["年齢", "性別", "客室クラス", "乗船港"]
        }
    """
    ...
```

#### 2.2.3 DB スキーマ拡張
```sql
ALTER TABLE competitions ADD COLUMN dataset_info TEXT;  -- JSON形式
ALTER TABLE competitions ADD COLUMN dataset_files TEXT;  -- ファイル一覧（カンマ区切り）
ALTER TABLE competitions ADD COLUMN dataset_size TEXT;   -- サイズ（例: "1.2 GB"）
```

**実装の類似性**:
- ✅ Overview タブと同じスクレイピング手法（Playwright）
- ✅ キャッシュ戦略も同様（1日 TTL）
- ✅ LLM で情報抽出・要約

---

### 2.3 ディスカッション情報の取得・整理

**現状の問題**:
- **Discussion タブ**（`/competitions/{id}/discussion`）は別ページ
- ディスカッション数は API で取得済み（`discussion_count`）
- ディスカッション内容や重要な投稿は未取得

**実装内容**:

#### 2.3.1 Discussion タブのスクレイピング
```python
# scraper_service.py に追加
def get_discussion_tab(self, comp_id: str) -> Optional[Dict[str, Any]]:
    """
    Discussion タブから情報を取得

    Returns:
        {
            'comp_id': 'titanic',
            'url': 'https://www.kaggle.com/competitions/titanic/discussion',
            'scraped_at': '2025-11-16T...',
            'discussion_text': '...'  # Discussion タブのテキスト全体
        }
    """
    url = f"{self.base_url}/{comp_id}/discussion"
    # Playwright でスクレイピング（Overview と同じ実装）
    ...
```

#### 2.3.2 LLM でディスカッション要約
```python
# llm_service.py に追加
def summarize_discussions(self, discussion_text: str, title: str = "") -> str:
    """
    Discussion タブのテキストから重要な議論を要約

    Returns:
        要約テキスト（例: "データリークに関する議論が活発。外れ値処理の工夫が必要。
        公式からデータ更新のアナウンスあり。"）
    """
    ...
```

#### 2.3.3 DB スキーマ拡張
```sql
ALTER TABLE competitions ADD COLUMN discussion_summary TEXT;
ALTER TABLE competitions ADD COLUMN discussion_updated_at TIMESTAMP;
```

**実装の類似性**:
- ✅ Data タブと同じスクレイピング手法（Playwright）
- ⚠️ **キャッシュ戦略**: 短い TTL（数時間〜半日）推奨（動的コンテンツのため）
- ✅ LLM で情報抽出・要約

---

### 📊 Phase 2 実装の優先順位（見直し後）

1. 🔴 **最優先**: 評価指標の抽出・保存
   - すぐ実装可能（メソッド追加のみ）
   - Overview タブの情報で完結

2. 🟡 **中優先**: Data タブのスクレイピング
   - **新規 URL** のスクレイピング（`/data`）
   - データセット情報を構造化
   - Overview と同様の実装パターン

3. 🟡 **中優先**: Discussion タブのスクレイピング
   - **新規 URL** のスクレイピング（`/discussion`）
   - 動的コンテンツ（短い TTL が必要）
   - Data タブと同様の実装パターン

**実装の共通パターン**:
```python
# scraper_service.py に汎用メソッドを追加
def get_tab_content(self, comp_id: str, tab: str) -> Optional[Dict[str, Any]]:
    """
    指定したタブのコンテンツを取得

    Args:
        comp_id: コンペティション ID
        tab: タブ名（'data', 'discussion', 'code', 'leaderboard'）

    Returns:
        スクレイピング結果
    """
    url = f"{self.base_url}/{comp_id}/{tab}" if tab else f"{self.base_url}/{comp_id}"
    # Playwright でスクレイピング（共通実装）
    ...
```

---

## 🎯 Phase 3: 動的コンテンツの対応（将来）

### 3.1 リーダーボード情報
- **更新頻度**: 高（コンペ開催中は日次更新）
- **キャッシュ戦略**: 短い TTL（数時間）
- **優先度**: 🟢 低（ユーザーは直接 Kaggle を見る）

### 3.2 新着ノートブック情報
- **更新頻度**: 高
- **キャッシュ戦略**: 短い TTL（数時間）
- **優先度**: 🟢 低

---

## 📊 3ステップ完了後の推奨フロー

```
Step 1-3 完了
   ↓
【確認】評価指標が保存されているか？
   ├─ Yes → Phase 3 へ
   └─ No  → Phase 2.1（評価指標抽出）を実装
      ↓
   Phase 2.1 実装 & テスト
      ↓
   【確認】データセット情報は要約に含まれているか？
      ├─ 十分 → Phase 2.3（ディスカッション）へ
      └─ 不足 → Phase 2.2（データセット情報）を改善
         ↓
      Phase 2.3（ディスカッション情報）
         ↓
      Phase 3（動的コンテンツ）は必要に応じて
```

---

## 🔍 確認チェックリスト

### Phase 1 完了後の確認

```sql
-- 1. 評価指標が保存されているか
SELECT id, title, metric
FROM competitions
WHERE metric IS NOT NULL AND metric != ''
LIMIT 10;

-- 2. 要約が生成されているか
SELECT id, title, LENGTH(summary) as summary_length
FROM competitions
WHERE summary IS NOT NULL AND summary != ''
LIMIT 10;

-- 3. タグが付与されているか
SELECT id, title, tags, data_types, domain
FROM competitions
WHERE tags IS NOT NULL AND tags != '[]'
LIMIT 10;

-- 4. スクレイピング日時が記録されているか
SELECT id, title, last_scraped_at
FROM competitions
WHERE last_scraped_at IS NOT NULL
ORDER BY last_scraped_at DESC
LIMIT 10;
```

### フロントエンドでの確認

- [ ] 要約が表示される
- [ ] タグが表示される（複数）
- [ ] データタイプが表示される
- [ ] ドメインが表示される
- [ ] **評価指標が表示される**（Phase 2.1 後）
- [ ] ディスカッション情報が表示される（Phase 2.3 後）

---

## 📝 次のアクション

### 即座に実行
1. ✅ Phase 1（Step 1-3）を完了
2. ✅ 上記の SQL でデータ確認
3. ✅ フロントエンドで表示確認

### 確認後の分岐
- **評価指標が空の場合** → Phase 2.1 を実装
- **データセット情報が不足の場合** → Phase 2.2 を検討
- **すべて十分な場合** → Phase 2.3（ディスカッション）へ

---

**作成日**: 2025-11-16
**次の優先タスク**: Phase 1（Step 1-3）の実行と確認
