# 4. 技術スタック

## 4.1 フロントエンド
- **フレームワーク**: Next.js 14+ (App Router)
- **言語**: TypeScript 5+
- **UIライブラリ**: React 18+
- **スタイリング**: Tailwind CSS
- **データフェッチング**: SWR または React Query
- **状態管理**: React Hooks (useState, useContext)
- **HTTPクライアント**: fetch API

## 4.2 バックエンド
- **言語**: Python 3.13
- **フレームワーク**: FastAPI 0.104+
- **データベース**:
  - **Phase 1**: SQLite 3（ローカル開発）
  - **Phase 2以降**: PostgreSQL 16+（Docker環境）
- **キャッシュ**:
  - **Phase 2以降**: Redis 7+（APIレスポンスキャッシュ、セッション管理）
- **ORM**: SQLAlchemy（オプション）または 素のSQL
- **Kaggle API**: kaggle 1.5.16+
- **LLM API**: OpenAI Python SDK (GPT-4o mini)
- **スクレイピング**: Playwright（Phase 2）
- **バリデーション**: Pydantic

## 4.3 インフラ・開発環境

### Phase 1（現在）: ローカル開発 ⚡
- **Python環境**: venv + uv（高速パッケージマネージャー）
- **データベース**: SQLite（ファイルベース、`kaggledb.db`）
- **開発サーバー**: uvicorn（バックエンド）、npm run dev（フロントエンド）
- **バージョン管理**: Git
- **環境変数管理**: .env

**特徴**:
- セットアップが超高速（`uv venv` + `npm install`）
- DBサーバー不要
- ホットリロード対応
- 学習・プロトタイピングに最適

### Phase 2以降: Docker環境 🐳
- **コンテナ**: Docker + Docker Compose
- **データベース**: PostgreSQL 16+（本番想定）
- **キャッシュ**: Redis 7+
- **オーケストレーション**: Docker Compose

**特徴**:
- 環境の一貫性（チーム開発対応）
- 本番環境に近い構成
- スケーラビリティ向上
- CI/CD パイプライン統合

## 4.4 開発ツール
- **フロントエンド**:
  - Node.js 20+
  - npm または yarn
  - ESLint + Prettier
  - TypeScript Compiler

- **バックエンド**:
  - pip
  - uvicorn（ASGIサーバー）
  - pytest（テスト、将来的に）

## 4.5 環境変数

### Phase 1: ローカル開発

**バックエンド (.env)**
```bash
# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# OpenAI API
OPENAI_API_KEY=your_openai_key

# Database（SQLite）
DATABASE_PATH=./data/kaggle_competitions.db

# Server
HOST=0.0.0.0
PORT=8000

# CORS（Next.jsからのアクセス許可）
CORS_ORIGINS=http://localhost:3000
```

**フロントエンド (.env.local)**
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Phase 2: Docker環境

**バックエンド (.env)**
```bash
# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# OpenAI API
OPENAI_API_KEY=your_openai_key

# Database（PostgreSQL）
DATABASE_URL=postgresql://kaggledb:password@postgres:5432/kaggledb
POSTGRES_USER=kaggledb
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=kaggledb

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600  # 1時間

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

**フロントエンド (.env.local)**
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 4.6 ディレクトリ構成

詳細は[ルートのREADME.md](../README.md#ディレクトリ構造)を参照してください。

---

**関連ドキュメント:**
- [システム概要](./01_overview.md)
- [Docker構成](./12_docker.md)
- [開発の始め方](./14_getting_started.md)
