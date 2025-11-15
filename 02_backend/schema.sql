-- ============================================
-- Kaggle Competition Knowledge Base
-- Database Schema (SQLite)
-- ============================================

-- 1. competitions テーブル
CREATE TABLE IF NOT EXISTS competitions (
    id                TEXT PRIMARY KEY,           -- Kaggle competition ID
    title             TEXT NOT NULL,              -- タイトル
    url               TEXT NOT NULL,              -- KaggleのURL
    start_date        DATE,                       -- 開始日
    end_date          DATE,                       -- 終了日
    status            TEXT NOT NULL,              -- 'active' or 'completed'
    metric            TEXT,                       -- 評価指標
    description       TEXT,                       -- 元の説明文（英語）
    summary           TEXT,                       -- LLM生成の和訳要約
    tags              TEXT,                       -- JSON配列
    data_types        TEXT,                       -- JSON配列
    domain            TEXT,                       -- ドメイン
    discussion_count  INTEGER DEFAULT 0,          -- ディスカッション数
    solution_status   TEXT DEFAULT '未着手',       -- ステータス
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 登録日時
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 更新日時
);

-- 2. discussions テーブル（Phase 2用）
CREATE TABLE IF NOT EXISTS discussions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id    TEXT NOT NULL,              -- 外部キー
    title             TEXT NOT NULL,              -- ディスカッションタイトル
    url               TEXT UNIQUE NOT NULL,       -- ディスカッションURL
    author            TEXT,                       -- 投稿者名
    author_tier       TEXT,                       -- Kaggle Tier
    author_medals     TEXT,                       -- JSON形式のメダル情報
    votes             INTEGER DEFAULT 0,          -- いいね数
    comment_count     INTEGER DEFAULT 0,          -- コメント数
    category          TEXT,                       -- LLM分類カテゴリ
    summary           TEXT,                       -- LLM生成要約
    key_points        TEXT,                       -- JSON配列
    content           TEXT,                       -- 本文（オプション）
    posted_at         TIMESTAMP,                  -- 投稿日時
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 登録日時
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新日時
    FOREIGN KEY (competition_id) REFERENCES competitions(id)
);

-- 3. solutions テーブル（Phase 3用）
CREATE TABLE IF NOT EXISTS solutions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id    TEXT NOT NULL,              -- 外部キー
    rank              INTEGER NOT NULL,           -- 順位（1-20）
    team_name         TEXT,                       -- チーム名
    score             REAL,                       -- スコア
    solution_url      TEXT,                       -- Solution投稿URL
    model             TEXT,                       -- モデル構成
    features          TEXT,                       -- 特徴量
    preprocessing     TEXT,                       -- 前処理
    cv_strategy       TEXT,                       -- CV戦略
    notes             TEXT,                       -- 特記事項
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 登録日時
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新日時
    FOREIGN KEY (competition_id) REFERENCES competitions(id)
);

-- 4. tags テーブル（マスタ）
CREATE TABLE IF NOT EXISTS tags (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT UNIQUE NOT NULL,       -- タグ名
    category          TEXT NOT NULL,              -- カテゴリID
    display_order     INTEGER DEFAULT 0,          -- 表示順
    description       TEXT                        -- タグの説明（オプション）
);

-- ============================================
-- インデックス
-- ============================================

-- competitions テーブル
CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions(status);
CREATE INDEX IF NOT EXISTS idx_competitions_end_date ON competitions(end_date);
CREATE INDEX IF NOT EXISTS idx_competitions_created_at ON competitions(created_at);

-- discussions テーブル
CREATE INDEX IF NOT EXISTS idx_discussions_competition_id ON discussions(competition_id);
CREATE INDEX IF NOT EXISTS idx_discussions_votes ON discussions(votes);
CREATE INDEX IF NOT EXISTS idx_discussions_posted_at ON discussions(posted_at);

-- solutions テーブル
CREATE INDEX IF NOT EXISTS idx_solutions_competition_id ON solutions(competition_id);
CREATE INDEX IF NOT EXISTS idx_solutions_rank ON solutions(rank);

-- tags テーブル
CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category);

-- ============================================
-- 初期データ（タグマスタ）
-- ============================================
-- カテゴリID一覧:
-- - data_type: データ種別
-- - task_type: タスク種別
-- - model_type: モデル種別
-- - solution_method: 解法種別
-- - competition_feature: コンペ特徴
-- - domain: ドメイン

INSERT OR IGNORE INTO tags (name, category, display_order) VALUES
-- データ種別 (data_type)
('テーブルデータ', 'data_type', 1),
('画像', 'data_type', 2),
('テキスト', 'data_type', 3),
('時系列', 'data_type', 4),
('音声', 'data_type', 5),
('動画', 'data_type', 6),
('マルチモーダル', 'data_type', 7),

-- タスク種別 (task_type)
('分類（二値）', 'task_type', 11),
('分類（多クラス）', 'task_type', 12),
('回帰', 'task_type', 13),
('ランキング', 'task_type', 14),
('物体検出', 'task_type', 15),
('セグメンテーション', 'task_type', 16),
('生成', 'task_type', 17),
('クラスタリング', 'task_type', 18),

-- モデル種別 (model_type)
('LightGBM', 'model_type', 21),
('XGBoost', 'model_type', 22),
('CatBoost', 'model_type', 23),
('Random Forest', 'model_type', 24),
('Neural Network', 'model_type', 25),
('CNN', 'model_type', 26),
('RNN', 'model_type', 27),
('LSTM', 'model_type', 28),
('Transformer', 'model_type', 29),
('BERT', 'model_type', 30),
('GPT', 'model_type', 31),
('U-Net', 'model_type', 32),
('YOLO', 'model_type', 33),
('Linear Model', 'model_type', 34),
('SVM', 'model_type', 35),

-- 解法種別 (solution_method)
('Stacking', 'solution_method', 41),
('Blending', 'solution_method', 42),
('Pseudo-Labeling', 'solution_method', 43),
('Adversarial Validation', 'solution_method', 44),
('Feature Selection', 'solution_method', 45),
('Target Encoding', 'solution_method', 46),
('Embedding', 'solution_method', 47),
('Augmentation', 'solution_method', 48),
('TTA (Test Time Augmentation)', 'solution_method', 49),
('Ensemble', 'solution_method', 50),
('Cross Validation', 'solution_method', 51),
('Fine-tuning', 'solution_method', 52),

-- コンペ特徴 (competition_feature)
('不均衡データ', 'competition_feature', 61),
('欠損値多い', 'competition_feature', 62),
('外れ値対策必要', 'competition_feature', 63),
('大規模データ', 'competition_feature', 64),
('小規模データ', 'competition_feature', 65),
('リーク対策必要', 'competition_feature', 66),
('時系列考慮', 'competition_feature', 67),
('ドメイン知識重要', 'competition_feature', 68),
('データ品質課題', 'competition_feature', 69),

-- ドメイン (domain)
('医療', 'domain', 71),
('金融', 'domain', 72),
('Eコマース', 'domain', 73),
('自然言語処理', 'domain', 74),
('コンピュータビジョン', 'domain', 75),
('音声認識', 'domain', 76),
('推薦システム', 'domain', 77),
('時系列予測', 'domain', 78),
('その他', 'domain', 79);
