# 7. API設計

## 7.1 基本仕様

**ベースURL**: `http://localhost:8000/api`

**認証**: なし（ローカル環境のため）

**レスポンス形式**: JSON

**CORS設定**: Next.js (localhost:3000) からのアクセスを許可

## 7.2 エンドポイント一覧

### 7.2.1 コンペ関連

**GET /api/competitions**

コンペ一覧取得（検索・フィルタ対応）

**クエリパラメータ:**
- `page`: int (ページ番号、デフォルト: 1)
- `limit`: int (1ページあたりの件数、デフォルト: 20)
- `search`: string (タイトル・タグ・要約で検索)
- `status`: string ('active' | 'completed' | 'all')
- `tags`: string[] (タグフィルタ、カンマ区切り)
- `metric`: string[] (評価指標フィルタ)
- `solution_status`: string ('未着手' | 'ディスカッションのみ' | '解法分析済み')
- `year`: int (開催年)
- `sort_by`: string ('end_date' | 'created_at' | 'title')
- `sort_order`: string ('asc' | 'desc')

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "titanic",
        "title": "Titanic - Machine Learning from Disaster",
        "url": "https://www.kaggle.com/c/titanic",
        "start_date": "2012-09-28",
        "end_date": "2030-12-31",
        "status": "active",
        "metric": "Accuracy",
        "summary": "タイタニック号の生存者予測...",
        "tags": ["テーブルデータ", "分類", "初心者向け"],
        "data_types": ["tabular"],
        "domain": "その他",
        "discussion_count": 125,
        "solution_status": "解法分析済み",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z"
      }
    ],
    "total": 500,
    "page": 1,
    "limit": 20,
    "total_pages": 25
  }
}
```

---

**GET /api/competitions/{id}**

コンペ詳細取得

**パスパラメータ:**
- `id`: string (コンペID)

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "id": "titanic",
    "title": "Titanic - Machine Learning from Disaster",
    "url": "https://www.kaggle.com/c/titanic",
    "start_date": "2012-09-28",
    "end_date": "2030-12-31",
    "status": "active",
    "metric": "Accuracy",
    "description": "英語の元説明文...",
    "summary": "日本語要約...",
    "tags": ["テーブルデータ", "分類"],
    "data_types": ["tabular"],
    "domain": "その他",
    "discussion_count": 125,
    "solution_status": "解法分析済み",
    "discussions": [],
    "solutions": [],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T00:00:00Z"
  }
}
```

---

**POST /api/competitions/refresh**

新規コンペを手動で取得（バッチ処理を手動実行）

**リクエストボディ:** なし

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "new_competitions": 5,
    "updated_competitions": 3
  }
}
```

---

**PUT /api/competitions/{id}/tags**

コンペのタグを更新

**パスパラメータ:**
- `id`: string (コンペID)

**リクエストボディ:**
```json
{
  "tags": ["テーブルデータ", "回帰", "時系列"]
}
```

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "id": "housing-prices",
    "tags": ["テーブルデータ", "回帰", "時系列"]
  }
}
```

### 7.2.2 ディスカッション関連（Phase 2）

**GET /api/competitions/{competition_id}/discussions**

コンペのディスカッション一覧取得

**パスパラメータ:**
- `competition_id`: string

**クエリパラメータ:**
- `category`: string[] (カテゴリフィルタ)
- `min_votes`: int (最小Vote数)
- `author_tier`: string ('all' | 'gold_medalist' | 'master_plus')
- `sort_by`: string ('votes' | 'posted_at')
- `sort_order`: string ('asc' | 'desc')

**レスポンス例:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "competition_id": "titanic",
      "title": "Feature Engineering Tips",
      "url": "https://www.kaggle.com/...",
      "author": "JohnDoe",
      "author_tier": "Grandmaster",
      "author_medals": {"gold": 3, "silver": 5, "bronze": 10},
      "votes": 245,
      "comment_count": 30,
      "category": "特徴量エンジニアリング",
      "summary": "効果的な特徴量の作り方...",
      "key_points": ["特徴量X", "特徴量Y", "特徴量Z"],
      "posted_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

**POST /api/competitions/{competition_id}/discussions/scrape**

ディスカッション一覧をスクレイピングで取得

**パスパラメータ:**
- `competition_id`: string

**リクエストボディ:**
```json
{
  "min_votes": 50,
  "include_gold_medalists": true
}
```

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "scraped_count": 25,
    "filtered_count": 15
  }
}
```

---

**POST /api/discussions**

ディスカッションを手動URLで追加

**リクエストボディ:**
```json
{
  "url": "https://www.kaggle.com/c/titanic/discussion/12345"
}
```

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Feature Engineering Tips",
    "category": "特徴量エンジニアリング",
    "summary": "..."
  }
}
```

---

**PUT /api/discussions/{id}**

ディスカッション情報更新（カテゴリ・要約など手動編集）

**パスパラメータ:**
- `id`: int

**リクエストボディ:**
```json
{
  "category": "モデル・手法",
  "summary": "修正した要約..."
}
```

---

**DELETE /api/discussions/{id}**

ディスカッション削除

**パスパラメータ:**
- `id`: int

### 7.2.3 解法関連（Phase 3）

**GET /api/competitions/{competition_id}/solutions**

コンペの上位解法一覧取得（1-20位）

**パスパラメータ:**
- `competition_id`: string

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "solutions": [
      {
        "id": 1,
        "rank": 1,
        "team_name": "Team Alpha",
        "score": 0.95234,
        "solution_url": "https://www.kaggle.com/...",
        "model": "LightGBM + NN",
        "features": "特徴量A, B, C...",
        "preprocessing": "欠損値補完、正規化...",
        "cv_strategy": "StratifiedKFold(5)",
        "notes": "..."
      }
    ],
    "analysis": {
      "common": {
        "almost_all": ["LightGBM", "TargetEncoding"],
        "majority": ["Stacking", "擬似ラベリング"],
        "effective_minority": ["特殊な特徴量X"]
      },
      "differentiation": {
        "top5_only": ["手法A", "工夫B"],
        "unique_approaches": []
      }
    }
  }
}
```

---

**POST /api/solutions**

解法を追加

**リクエストボディ:**
```json
{
  "competition_id": "titanic",
  "rank": 1,
  "team_name": "Team Alpha",
  "score": 0.95234,
  "solution_url": "https://...",
  "model": "LightGBM + NN",
  "features": "...",
  "preprocessing": "...",
  "cv_strategy": "...",
  "notes": "..."
}
```

**PUT /api/solutions/{id}** - 解法更新  
**DELETE /api/solutions/{id}** - 解法削除

### 7.2.4 統計・ダッシュボード関連

**GET /api/stats/summary**

サマリー統計取得

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "total_competitions": 452,
    "active_competitions": 12,
    "completed_competitions": 440
  }
}
```

---

**GET /api/stats/yearly**

年別コンペ数取得

**クエリパラメータ:**
- `start_year`: int (開始年、デフォルト: 2020)

**レスポンス例:**
```json
{
  "status": "success",
  "data": [
    { "year": 2020, "count": 85 },
    { "year": 2021, "count": 95 },
    { "year": 2022, "count": 105 },
    { "year": 2023, "count": 92 },
    { "year": 2024, "count": 75 }
  ]
}
```

---

**GET /api/stats/data-types**

データ種別の分布取得

**レスポンス例:**
```json
{
  "status": "success",
  "data": [
    { 
      "type": "tabular", 
      "label": "テーブル",
      "count": 200 
    },
    { 
      "type": "image", 
      "label": "画像",
      "count": 150 
    },
    { 
      "type": "text", 
      "label": "テキスト",
      "count": 100 
    },
    { 
      "type": "time-series", 
      "label": "時系列",
      "count": 65 
    },
    { 
      "type": "audio", 
      "label": "音声",
      "count": 25 
    },
    { 
      "type": "video", 
      "label": "動画",
      "count": 12 
    }
  ],
  "multi_modal_count": 35
}
```

---

**GET /api/competitions/active**

開催中のコンペ一覧取得（カード表示用）

**クエリパラメータ:**
- `limit`: int (取得件数、デフォルト: 12、最大: 20)
- `sort_by`: string ('deadline' | 'created_at', デフォルト: 'deadline')

**レスポンス例:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "housing-prices-2025",
      "title": "Housing Prices Prediction 2025",
      "url": "https://www.kaggle.com/c/housing-prices-2025",
      "end_date": "2025-01-15T23:59:59Z",
      "days_remaining": 15,
      "status": "active",
      "summary": "住宅価格を予測するコンペ。79個の特徴量を使った回帰タスク。初心者にも取り組みやすい課題。",
      "metric": "RMSE",
      "tags": ["テーブルデータ", "回帰", "特徴量エンジニアリング"],
      "data_types": ["tabular"]
    }
  ],
  "total": 12
}
```

### 7.2.5 マスタ関連

**GET /api/tags**

タグ一覧取得

**クエリパラメータ:**
- `category`: string (タグカテゴリでフィルタ)

**レスポンス例:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "不均衡データ",
      "category": "課題系",
      "display_order": 0
    }
  ]
}
```

---

**GET /api/metrics**

評価指標一覧取得

**レスポンス例:**
```json
{
  "status": "success",
  "data": [
    "AUC", "F1", "Accuracy", "RMSE", "MAE", 
    "LogLoss", "MAP@K", "Dice", "IoU"
  ]
}
```

## 7.3 エラーレスポンス

**形式:**
```json
{
  "status": "error",
  "message": "エラーメッセージ",
  "code": "ERROR_CODE",
  "detail": {}
}
```

**エラーコード例:**
- `COMPETITION_NOT_FOUND`: コンペが見つからない
- `INVALID_PARAMETER`: 不正なパラメータ
- `KAGGLE_API_ERROR`: Kaggle API エラー
- `LLM_API_ERROR`: OpenAI API エラー
- `DATABASE_ERROR`: データベースエラー

---

**関連ドキュメント:**
- [機能要件](./02_requirements.md)
- [データ設計](./03_data_design.md)
- [バックエンド仕様](./11_backend_spec.md)
- [フロントエンド仕様](./10_frontend_spec.md)
