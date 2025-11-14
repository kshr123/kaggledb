# Kaggle情報収集ツール - プロジェクト固有ルール

> このファイルは**このプロジェクト固有**のルールです。汎用的な開発ルールは [general_rules.md](./general_rules.md) を参照してください。

---

## 📁 ディレクトリ構造とルール

### ディレクトリの役割

```
.
├── src/                    # メインソースコード
│   ├── api/               # Kaggle API クライアント
│   ├── database/          # データベース操作
│   ├── models/            # データモデル（SQLAlchemy）
│   └── utils/             # ユーティリティ関数
├── tests/                  # テストコード
│   ├── unit/              # ユニットテスト
│   ├── integration/       # 統合テスト
│   └── fixtures/          # テストデータ
├── docs/                   # ドキュメント・仕様書
│   ├── SPECIFICATION.md   # 全体仕様
│   └── api/               # API仕様
├── scripts/                # ユーティリティスクリプト
│   └── setup_db.py        # DB初期化スクリプト
├── config/                 # 設定ファイル
└── .env.example            # 環境変数サンプル
```

### 重要なルール

#### 1. `src/` にメインコードを配置

- **Pythonパッケージ構造**: 各ディレクトリに `__init__.py` を配置
- **モジュール分割**: 機能ごとに適切にファイルを分ける
- **命名規則**:
  - ✅ `kaggle_client.py`, `database_manager.py`
  - ❌ `01_client.py`（数字で始まるとimportできない）

#### 2. `tests/` にテストコードを配置

- **テスト命名**: `test_*.py` の形式
- **テストの種類**:
  - `unit/` - 個々の関数・クラスの単体テスト
  - `integration/` - DB接続やAPI呼び出しを含む統合テスト
  - `fixtures/` - テストデータ、モックデータ
- **pytest使用**: テストフレームワークはpytest

#### 3. `docs/` にドキュメントを配置

- **SPECIFICATION.md**: 全体仕様を記載
  - 要件定義
  - システムアーキテクチャ
  - データモデル
  - API設計
- **README.md**: プロジェクト概要とセットアップ手順

#### 4. `scripts/` にユーティリティスクリプトを配置

- データベース初期化スクリプト
- データマイグレーションスクリプト
- バッチ処理スクリプト

---

## 💻 このプロジェクト特有のコーディング規約

### Python

- **バージョン**: Python 3.13以上（最新の安定版を使用）
- **パッケージマネージャー**: uv（高速・モダンなパッケージマネージャー）
- **コメントとdocstringの言語**: **必ず日本語で記載すること**
  - ✅ モジュールdocstring: 日本語
  - ✅ 関数/クラスdocstring: 日本語
  - ✅ インラインコメント: 日本語
  - ❌ 英語のコメントは使用しない

#### 主要ライブラリ

```python
# Kaggle API クライアント
import kaggle

# データベース（SQLAlchemy）
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 環境変数管理
from dotenv import load_dotenv
import os

# テスト
import pytest
```

#### uvの使い方

```bash
# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate  # macOS/Linux

# 依存関係のインストール
uv pip install kaggle psycopg2-binary sqlalchemy pytest pytest-cov

# 開発ツールのインストール
uv pip install black ruff mypy
```

### ファイル構成

プロジェクトには以下のファイルを含める：

#### 必須ファイル

- `docs/SPECIFICATION.md` - **仕様書**（要件、アーキテクチャ、データモデル）
- `README.md` - プロジェクト概要、セットアップ手順、使用方法
- `pyproject.toml` - プロジェクトメタデータと依存関係
- `.env.example` - 環境変数のサンプル（API キー等）
- `tests/` - テストコード
  - `unit/test_*.py` - ユニットテスト
  - `integration/test_*.py` - 統合テスト

#### 自動生成ファイル

- `uv.lock` - 依存関係のロックファイル（自動生成、Git管理）

#### オプションファイル

- `.python-version` - Pythonバージョンの指定
- `docker-compose.yml` - Docker環境（PostgreSQL等）
- `Makefile` - よく使うコマンドのショートカット
- `.gitignore` - Git管理除外ファイル


---

## 🔑 Kaggle API の使用方法

### API認証設定

Kaggle APIを使用するには、APIキーが必要です。

1. **Kaggleアカウントページ**から `kaggle.json` をダウンロード
2. **配置場所**: `~/.kaggle/kaggle.json`
3. **権限設定**: `chmod 600 ~/.kaggle/kaggle.json`

### 環境変数による管理（推奨）

```bash
# .env ファイルに記載
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### 主な操作

```python
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# コンペティション一覧取得
competitions = api.competitions_list()

# データセット一覧取得
datasets = api.datasets_list()

# ノートブック一覧取得
notebooks = api.kernels_list()
```

---

## 🗄️ データベース管理

### PostgreSQL設定

#### Docker Composeでの起動（推奨）

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: kaggledb
      POSTGRES_USER: kaggle_user
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

#### 環境変数

```bash
# .env
DATABASE_URL=postgresql://kaggle_user:your_password@localhost:5432/kaggledb
```

### データモデル設計

SQLAlchemyを使用してデータモデルを定義：

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Competition(Base):
    """Kaggleコンペティション情報"""
    __tablename__ = 'competitions'

    id = Column(Integer, primary_key=True)
    ref = Column(String(255), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime)
    reward = Column(Integer)
    is_active = Column(Boolean, default=True)
    # ...
```

### マイグレーション

データベーススキーマの変更はAlembicで管理：

```bash
# マイグレーションファイル作成
alembic revision --autogenerate -m "Add competitions table"

# マイグレーション実行
alembic upgrade head
```

---

## 🔒 セキュリティとAPIキー管理

### 重要な原則

❌ **絶対にやってはいけないこと**:
- APIキーをコードに直接書く
- `.env` ファイルをGitにコミットする
- APIキーをログに出力する
- データベース接続情報をハードコード

✅ **推奨事項**:
- `.env.example` を用意（値は空またはダミー）
- `.gitignore` に `.env` を追加
- 環境変数から読み込む
- `python-dotenv` を使用

### .env.example の例

```bash
# Kaggle API
KAGGLE_USERNAME=your_username_here
KAGGLE_KEY=your_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/kaggledb

# Application
DEBUG=False
LOG_LEVEL=INFO
```

### .gitignore設定

```gitignore
# 環境変数ファイル
.env
.env.local
.env.*.local

# APIキー
kaggle.json
*.key
*.pem

# データベース
*.db
*.sqlite
*.sqlite3

# データ
data/raw/
data/processed/
*.csv
*.json
!.env.example
```

---

## 📊 ドキュメント管理

### 必須ドキュメント

1. **README.md** - プロジェクト概要
   - プロジェクトの目的
   - セットアップ手順
   - 使用方法
   - 技術スタック

2. **docs/SPECIFICATION.md** - 詳細仕様
   - 要件定義
   - システムアーキテクチャ
   - データモデル
   - API設計

3. **CHANGELOG.md** - 変更履歴（オプション）
   - 機能追加
   - バグ修正
   - 破壊的変更

### ドキュメント更新フロー

機能追加時：
1. **SPECIFICATION.md** を更新（設計）
2. 実装
3. **README.md** を更新（使い方）
4. Git コミット・プッシュ

---

## 🤝 Claude Codeとの協働ルール（プロジェクト固有）

### このプロジェクトで Claude Code に期待すること

1. **仕様策定支援**: SPECIFICATION.mdの作成補助
2. **設計支援**: データモデル、アーキテクチャの提案
3. **実装サポート**: Kaggle API クライアント、DB操作の実装
4. **テスト作成**: ユニットテスト、統合テストの作成
5. **レビュー**: コードの改善提案
6. **トラブルシューティング**: エラーの解決支援

### Claude Code が守るべきこと（プロジェクト固有）

1. **セキュリティ第一**:
   - APIキーをコードに書かない
   - 環境変数で管理
   - `.gitignore` の適切な設定

2. **テスト駆動開発**:
   - まず失敗するテストを書く（Red）
   - 最小限の実装でGreenにする
   - リファクタリング

3. **日本語ドキュメント**:
   - コメント、docstringは日本語
   - README、SPECIFICATIONも日本語

4. **PostgreSQL MCPの活用**:
   - スキーマ設計時にMCPを使用
   - クエリの最適化

### Claude Codeへの指示例

#### 良い指示（仕様駆動 + TDD）:

**フェーズ1: 仕様策定**
- "KaggleDBのSPECIFICATION.mdを作成して。要件定義から始めて"
- "データモデル（Competition, Dataset, Notebook）を設計して"

**フェーズ2: テスト作成**
- "Kaggle APIクライアントのユニットテストを作成して。まず失敗するテストから"
- "データベース操作の統合テストを追加して"

**フェーズ3: 実装**
- "最初のテストを通すための最小限の実装をして"
- "次の機能を実装して、テストを段階的にGreenにして"

**フェーズ4: リファクタリング**
- "実装をレビューして、改善点を提案して"
- "PostgreSQL MCPを使ってクエリを最適化して"

#### 悪い指示：
- "全部一気に実装して" ← TDDサイクルを無視
- "テストは後で書く" ← テスト駆動開発ではない
- "仕様書は不要" ← 仕様駆動開発ではない
- "APIキーをコードに書いて" ← セキュリティ違反

---

**最終更新**: 2025-11-15
