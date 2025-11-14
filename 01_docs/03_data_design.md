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
category          TEXT NOT NULL          # カテゴリ
display_order     INTEGER DEFAULT 0      # 表示順
```

## 3.2 タグ一覧（初期データ）

**課題系**
- 不均衡データ
- 異常検知
- 欠損値
- 時系列
- マルチモーダル

**データ系**
- テーブルデータ
- 画像
- テキスト
- 音声
- 動画

**手法系**
- アンサンブル
- Transformer
- GBM
- 深層学習
- 擬似ラベリング

**ドメイン系**
- 医療
- 金融
- Eコマース
- 自然言語処理
- コンピュータビジョン

---

**関連ドキュメント:**
- [機能要件](./02_requirements.md)
- [技術スタック](./04_tech_stack.md)
- [バックエンド仕様](./11_backend_spec.md)
