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
    category          TEXT NOT NULL,              -- カテゴリ
    display_order     INTEGER DEFAULT 0           -- 表示順
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

INSERT OR IGNORE INTO tags (name, category, display_order) VALUES
-- 課題系
('不均衡データ', '課題系', 1),
('異常検知', '課題系', 2),
('欠損値', '課題系', 3),
('時系列', '課題系', 4),
('マルチモーダル', '課題系', 5),

-- データ系
('テーブルデータ', 'データ系', 11),
('画像', 'データ系', 12),
('テキスト', 'データ系', 13),
('音声', 'データ系', 14),
('動画', 'データ系', 15),

-- 手法系
('アンサンブル', '手法系', 21),
('Transformer', '手法系', 22),
('GBM', '手法系', 23),
('深層学習', '手法系', 24),
('擬似ラベリング', '手法系', 25),

-- ドメイン系
('医療', 'ドメイン系', 31),
('金融', 'ドメイン系', 32),
('Eコマース', 'ドメイン系', 33),
('自然言語処理', 'ドメイン系', 34),
('コンピュータビジョン', 'ドメイン系', 35);
