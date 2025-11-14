# Kaggle Competition Knowledge Base

Kaggleのコンペ情報、ディスカッション、上位解法を体系的に管理・検索できるナレッジベースシステム

## 📋 プロジェクト概要

このシステムは、Kaggleのコンペ情報を自動取得・整理し、効率的に検索・分析できるWebアプリケーションです。

### 主な機能

- 📊 **コンペ情報管理**: Kaggle APIで自動取得、LLMで日本語要約・タグ生成
- 🔍 **高度な検索・フィルタ**: タグ、データ種別、評価指標、開催年などで絞り込み
- 📈 **ダッシュボード**: 統計情報の可視化、開催中コンペの一覧表示
- 💬 **ディスカッション管理** (Phase 2): Kaggleフォーラムの重要な投稿を整理
- 🏆 **上位解法分析** (Phase 3): 1-20位の解法を比較分析

### 技術スタック

**フロントエンド**
- Next.js 14+ (App Router)
- TypeScript 5+
- Tailwind CSS
- SWR / React Query

**バックエンド**
- Python 3.13
- FastAPI 0.104+
- SQLite 3
- Kaggle API
- OpenAI API (GPT-4o mini)
- Playwright (スクレイピング)

**開発環境**
- Docker + Docker Compose
- uv (Pythonパッケージマネージャー)

## 🚀 クイックスタート

### 前提条件

- Docker & Docker Compose
- Kaggle API認証 (`~/.kaggle/kaggle.json`)
- OpenAI API キー

### セットアップ

```bash
# 1. リポジトリクローン
git clone <repository-url>
cd kaggledb

# 2. 環境変数設定
cp 02_backend/.env.example 02_backend/.env
cp .env.local.example .env.local
# .env ファイルを編集してAPI Keyを設定

# 3. Docker起動
docker-compose up -d

# 4. DB初期化（初回のみ）
docker-compose exec backend python app/batch/init_db.py

# 5. コンペ情報取得（初回のみ、時間かかる）
docker-compose exec backend python app/batch/fetch_competitions.py
```

### アクセス

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

## 📁 ディレクトリ構造

```
kaggledb/
├── docker-compose.yml       # Docker Compose 設定
├── package.json             # Next.js 依存関係
├── tsconfig.json            # TypeScript 設定
├── next.config.js           # Next.js 設定
├── tailwind.config.ts       # Tailwind CSS 設定
├── .gitignore
├── .env.local.example       # フロントエンド環境変数サンプル
├── README.md
│
├── 01_docs/                 # ドキュメント
│   ├── README.md            # ドキュメントインデックス
│   ├── 01_overview.md       # プロジェクト概要
│   ├── 02_requirements.md   # 機能要件
│   ├── 03_data_design.md    # データ設計
│   └── ...                  # 各種仕様書
│
├── 02_backend/              # FastAPI バックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   ├── schema.sql
│   ├── app/
│   │   ├── main.py          # FastAPI アプリ
│   │   ├── config.py        # 設定管理
│   │   ├── database.py      # DB接続
│   │   ├── models.py        # Pydanticモデル
│   │   ├── routers/         # API エンドポイント
│   │   ├── services/        # ビジネスロジック
│   │   └── batch/           # バッチ処理
│   ├── tests/               # テスト
│   │   ├── test_*.py
│   │   └── test_results/    # テスト結果
│   └── data/                # データベース
│
├── 03_frontend/             # Next.js フロントエンド (App Router)
│   ├── app/                 # ページ
│   │   ├── layout.tsx       # ルートレイアウト
│   │   ├── page.tsx         # ホーム画面
│   │   └── competitions/    # コンペ詳細
│   ├── components/          # React コンポーネント
│   │   ├── dashboard/       # ダッシュボード関連
│   │   ├── CompetitionTable.tsx
│   │   ├── FilterPanel.tsx
│   │   └── ...
│   ├── lib/                 # ユーティリティ・APIクライアント
│   └── types/               # TypeScript 型定義
│
├── public/                  # Next.js 静的ファイル
│
├── 04_scripts/              # ユーティリティスクリプト
│
├── 05_progress/             # 開発進捗
│   └── progress_log.md
│
├── .claude/                 # Claude Code 設定
│   ├── CLAUDE.md
│   ├── project_rules.md
│   ├── general_rules.md
│   ├── folder_structure_rules.md
│   ├── test_management_rules.md
│   └── settings.local.json
│
└── .mcp.json                # MCP設定
```

## 📖 ドキュメント

- **詳細仕様**: [01_docs/README.md](./01_docs/README.md)（分割版仕様書）
- **開発ルール**: [.claude/CLAUDE.md](./.claude/CLAUDE.md)
- **フォルダ構成**: [.claude/folder_structure_rules.md](./.claude/folder_structure_rules.md)
- **開発進捗**: [05_progress/progress_log.md](./05_progress/progress_log.md)

## 🔧 開発コマンド

```bash
# ログ確認
docker-compose logs -f

# コンテナ再起動
docker-compose restart

# コンテナ停止
docker-compose down

# バックエンドのみ再ビルド
docker-compose up -d --build backend

# フロントエンドのみ再ビルド
docker-compose up -d --build frontend

# 新規コンペ取得（手動実行）
docker-compose exec backend python app/batch/fetch_competitions.py

# DB リセット
docker-compose exec backend python app/batch/init_db.py --reset
```

## 📊 開発フェーズ

### Phase 0: プロジェクトセットアップ ✅
- Claude Code設定
- MCP設定（Kaggle, SQLite, PostgreSQL, GitHub, Playwright等）
- 仕様書作成

### Phase 1: MVP（基本機能） 🚧
- コンペ情報管理
- ホーム画面（検索・フィルタ・ダッシュボード）
- コンペ詳細画面

### Phase 2: ディスカッション機能 📋
- Playwrightでスクレイピング
- LLMでカテゴリ分類・要約
- ディスカッション表示・フィルタ

### Phase 3: 上位解法分析 🏆
- 1-20位の解法記録
- 共通点・差別化ポイントの分析
- 分析結果の可視化

## 🛠️ 技術仕様

### データベース（SQLite）

- `competitions` - コンペ基本情報
- `discussions` - ディスカッション情報
- `solutions` - 上位解法情報
- `tags` - タグマスタ

### API エンドポイント

- `GET /api/competitions` - コンペ一覧取得
- `GET /api/competitions/{id}` - コンペ詳細取得
- `POST /api/competitions/refresh` - 新規コンペ取得
- `GET /api/stats/summary` - サマリー統計
- `GET /api/stats/yearly` - 年別統計
- `GET /api/stats/data-types` - データ種別分布

詳細は [docs/SPECIFICATION.md](./docs/SPECIFICATION.md) を参照

## 🔌 MCP (Model Context Protocol)

このプロジェクトでは以下のMCPサーバーを利用：

- **Kaggle MCP**: Kaggle API との直接連携
- **SQLite MCP**: 開発・テスト用DB
- **PostgreSQL MCP**: 本番用DB
- **GitHub MCP**: リポジトリ管理
- **Serena MCP**: コード分析
- **Context7 MCP**: ドキュメント参照
- **Playwright MCP**: ブラウザ自動化
- **Notion MCP**: メモ管理（オプション）

設定: `.mcp.json`

## 🤝 開発プロセス

1. **仕様駆動開発（SDD）**: まず仕様を明確化
2. **テスト駆動開発（TDD）**: Red → Green → Refactor
3. **AI駆動開発**: Claude Code と協働

詳細は [.claude/general_rules.md](./.claude/general_rules.md) を参照

## 📝 ライセンス

MIT License

---

**プロジェクト開始**: 2025-11-15
**作成者**: daisakura
**仕様バージョン**: 2.0
