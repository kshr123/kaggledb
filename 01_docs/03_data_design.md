# 3. データ設計

## 3.1 データベース（SQLite）

### 3.1.1 competitions テーブル
```
id                TEXT PRIMARY KEY       # Kaggle competition ID
title             TEXT NOT NULL          # タイトル
url               TEXT NOT NULL          # KaggleのURL
start_date        DATE                   # 開始日
end_date          DATE                   # 終了日
status            TEXT NOT NULL          # 'active' or 'completed'
metric            TEXT                   # 評価指標
description       TEXT                   # 元の説明文（英語）
summary           TEXT                   # LLM生成の和訳要約
tags              TEXT                   # JSON配列
data_types        TEXT                   # JSON配列
domain            TEXT                   # ドメイン
discussion_count  INTEGER DEFAULT 0      # ディスカッション数
solution_status   TEXT DEFAULT '未着手'   # ステータス
created_at        TIMESTAMP              # 登録日時
updated_at        TIMESTAMP              # 更新日時
```

### 3.1.2 discussions テーブル
```
id                INTEGER PRIMARY KEY AUTOINCREMENT
competition_id    TEXT NOT NULL          # 外部キー
title             TEXT NOT NULL          # ディスカッションタイトル
url               TEXT UNIQUE NOT NULL   # ディスカッションURL
author            TEXT                   # 投稿者名
author_tier       TEXT                   # Kaggle Tier
author_medals     TEXT                   # JSON形式のメダル情報
votes             INTEGER DEFAULT 0      # いいね数
comment_count     INTEGER DEFAULT 0      # コメント数
category          TEXT                   # LLM分類カテゴリ
summary           TEXT                   # LLM生成要約
key_points        TEXT                   # JSON配列
content           TEXT                   # 本文（オプション）
posted_at         TIMESTAMP              # 投稿日時
created_at        TIMESTAMP              # 登録日時
updated_at        TIMESTAMP              # 更新日時
```

### 3.1.3 solutions テーブル
```
id                INTEGER PRIMARY KEY AUTOINCREMENT
competition_id    TEXT NOT NULL          # 外部キー
rank              INTEGER NOT NULL       # 順位（1-20）
team_name         TEXT                   # チーム名
score             REAL                   # スコア
solution_url      TEXT                   # Solution投稿URL
model             TEXT                   # モデル構成
features          TEXT                   # 特徴量
preprocessing     TEXT                   # 前処理
cv_strategy       TEXT                   # CV戦略
notes             TEXT                   # 特記事項
created_at        TIMESTAMP              # 登録日時
updated_at        TIMESTAMP              # 更新日時
```

### 3.1.4 tags テーブル（マスタ）
```
id                INTEGER PRIMARY KEY AUTOINCREMENT
name              TEXT UNIQUE NOT NULL   # タグ名
category          TEXT NOT NULL          # カテゴリID
display_order     INTEGER DEFAULT 0      # 表示順
description       TEXT                   # タグの説明（オプション）
```

**カテゴリ値**:
- `data_type` - データ種別
- `task_type` - タスク種別
- `model_type` - モデル種別
- `solution_method` - 解法種別
- `competition_feature` - コンペ特徴
- `domain` - ドメイン

## 3.2 タグカテゴリと初期データ

### カテゴリ定義

| カテゴリID | カテゴリ名 | 説明 | フィルタ表示順 |
|-----------|----------|------|--------------|
| data_type | データ種別 | データの形式 | 1 |
| task_type | タスク種別 | 解くべき課題の種類 | 2 |
| model_type | モデル種別 | 使用するモデル | 3 |
| solution_method | 解法種別 | テクニック・手法 | 4 |
| competition_feature | コンペ特徴 | データセットの特性 | 5 |
| domain | ドメイン | 応用分野 | 6 |

### 初期タグデータ

**データ種別（data_type）**
- テーブルデータ
- 画像
- テキスト
- 時系列
- 音声
- 動画
- マルチモーダル

**タスク種別（task_type）**
- 分類（二値）
- 分類（多クラス）
- 回帰
- ランキング
- 物体検出
- セグメンテーション
- 生成
- クラスタリング

**モデル種別（model_type）**
- LightGBM
- XGBoost
- CatBoost
- Random Forest
- Neural Network
- CNN
- RNN
- LSTM
- Transformer
- BERT
- GPT
- U-Net
- YOLO
- Linear Model
- SVM

**解法種別（solution_method）**
- Stacking
- Blending
- Pseudo-Labeling
- Adversarial Validation
- Feature Selection
- Target Encoding
- Embedding
- Augmentation
- TTA (Test Time Augmentation)
- Ensemble
- Cross Validation
- Fine-tuning

**コンペ特徴（competition_feature）**
- 不均衡データ
- 欠損値多い
- 外れ値対策必要
- 大規模データ
- 小規模データ
- リーク対策必要
- 時系列考慮
- ドメイン知識重要
- データ品質課題

**ドメイン（domain）**
- 医療
- 金融
- Eコマース
- 自然言語処理
- コンピュータビジョン
- 音声認識
- 推薦システム
- 時系列予測
- その他

## 3.3 レコメンド機能のデータ設計

### 3.3.1 competition_views テーブル（オプション・将来拡張用）
```
id                INTEGER PRIMARY KEY AUTOINCREMENT
competition_id    TEXT NOT NULL          # 外部キー
user_id           TEXT                   # ユーザーID（将来用）
viewed_at         TIMESTAMP              # 閲覧日時
```

**現在はローカルストレージベースで実装**:
- ブラウザのlocalStorageに閲覧履歴を保存
- サーバー側ではタグベースの類似度計算のみ

### 3.3.2 レコメンドロジック

**1. タグ類似度スコア**:
```
similarity_score = (共通タグ数) / (全体タグ数)
重み付け:
  - data_type: 1.0
  - task_type: 1.5 (重要)
  - model_type: 1.2
  - solution_method: 1.3
  - competition_feature: 0.8
  - domain: 1.0
```

**2. 新規コンペ判定**:
- `created_at >= (現在時刻 - 30日)` のコンペ

**3. トレンドスコア**:
- 最近追加されたコンペに高スコア
- `days_since_created = 現在時刻 - created_at`
- `trend_score = 1.0 / (1 + days_since_created / 7)`

---

**関連ドキュメント:**
- [機能要件](./02_requirements.md)
- [技術スタック](./04_tech_stack.md)
- [バックエンド仕様](./11_backend_spec.md)
- [API設計](./07_api_design.md)
