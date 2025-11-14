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
- **データベース**: SQLite 3
- **ORM**: SQLAlchemy（オプション）または 素のSQL
- **Kaggle API**: kaggle 1.5.16+
- **LLM API**: OpenAI Python SDK (GPT-4o mini)
- **スクレイピング**: Playwright（Phase 2）
- **バリデーション**: Pydantic

## 4.3 インフラ・開発環境
- **コンテナ**: Docker + Docker Compose
- **バージョン管理**: Git
- **環境変数管理**: .env

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

**バックエンド (.env)**
```bash
# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# OpenAI API
OPENAI_API_KEY=your_openai_key

# Database
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

## 4.6 ディレクトリ構成

詳細は[ルートのREADME.md](../README.md#ディレクトリ構造)を参照してください。

---

**関連ドキュメント:**
- [システム概要](./01_overview.md)
- [Docker構成](./12_docker.md)
- [開発の始め方](./14_getting_started.md)
