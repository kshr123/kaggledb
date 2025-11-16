# Kaggle情報収集ツール - KaggleDB

> **このプロジェクトについて**: Kaggleのコンペティション、データセット、ノートブック情報を効率的に収集・管理する自分用ツールです。

---

## 📋 プロジェクト概要

このプロジェクトは以下の3つの柱で構成されています：

1. **仕様駆動開発（SDD）** - まず仕様を明確にしてから実装
2. **テスト駆動開発（TDD）** - Red→Green→Refactorのサイクル
3. **継続的な改善** - 実際に使いながら機能を拡張

### プロジェクトの目的

- Kaggle API を活用して情報を自動収集する
- PostgreSQLでデータを効率的に管理する
- コンペティションのトレンド分析や検索機能を提供する
- 自分の学習・分析効率を向上させる

---

## 📁 ディレクトリ構造

```
.
├── src/                    # メインソースコード
│   ├── api/               # Kaggle API クライアント
│   ├── database/          # データベース操作
│   ├── models/            # データモデル
│   └── utils/             # ユーティリティ
├── tests/                  # テストコード
│   ├── unit/              # ユニットテスト
│   ├── integration/       # 統合テスト
│   └── fixtures/          # テストデータ
├── docs/                   # ドキュメント・仕様書
│   ├── SPECIFICATION.md   # 全体仕様
│   └── api/               # API仕様
├── scripts/                # ユーティリティスクリプト
│   └── setup_db.sql       # DB初期化スクリプト
├── config/                 # 設定ファイル
└── .env.example            # 環境変数サンプル
```

---

## 🚀 クイックスタート

### 初回セットアップ

```bash
# 1. プロジェクトディレクトリに移動
cd /Users/kotaro/Desktop/dev/kaggledb

# 2. 仮想環境セットアップ
echo "3.13" > .python-version
uv venv
source .venv/bin/activate

# 3. 依存関係インストール
uv pip install kaggle psycopg2-binary sqlalchemy pytest pytest-cov black ruff mypy

# 4. 環境変数設定
cp .env.example .env
# .env を編集して Kaggle API キーとDB接続情報を設定

# 5. PostgreSQL起動（Docker使用の場合）
docker run -d \
  --name kaggledb-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=kaggledb \
  -p 5432:5432 \
  postgres:16

# 6. データベース初期化
python scripts/setup_db.py
```

### 開発フロー

```
仕様策定 → テスト作成(Red) → 実装(Green) → リファクタリング → 検証 → 振り返り
```

詳細は [project_rules.md](./project_rules.md) を参照してください。

---

## 📚 ルールファイル構成

このプロジェクトのルールは3つのファイルに分かれています：

### 1. このファイル (CLAUDE.md)
- プロジェクト概要
- クイックリファレンス
- ルールファイルの構成

### 2. [project_rules.md](./project_rules.md)
**このプロジェクト固有のルール**
- ディレクトリ構造とルール（詳細）
- Kaggle API の使用方法
- データベース管理ルール
- データモデル設計
- セキュリティとAPI キー管理
- 進捗管理とドキュメント

### 3. [general_rules.md](./general_rules.md)
**どんなプロジェクトでも使える汎用的なルール**
- 仕様駆動開発（SDD）
- テスト駆動開発（TDD）
- コーディング規約
- セキュリティ・パフォーマンス
- Git管理
- Claude Codeとの協働ルール

**重要**: `general_rules.md`は他のプロジェクト（Webアプリ、データサイエンス、DevOpsなど）でもそのまま使えます。

---

## 🎯 プロジェクトステータス

- **開始日**: 2025-11-15
- **現在のフェーズ**: Phase 2 開発中（検索・分析機能）
- **次のステップ**: フィルタリング機能、自動化処理の実装

---

## 🗺️ 開発ロードマップ

### Phase 1: 基本機能（MVP）✅
- [x] Kaggle API クライアント実装
- [x] PostgreSQLデータベース設定
- [x] コンペティション情報の収集
- [x] 基本的なCRUD操作
- [x] Webスクレイピング（Playwright）によるディスカッション/ランキング取得

### Phase 2: 検索・分析機能（進行中）
- [x] Solutions機能（終了済みコンペの解法整理）
  - [x] ディスカッションからの解法自動識別（タイトルパターンマッチング）
  - [x] LLM要約生成（OpenAI GPT-4o-mini）
  - [x] 構造化サマリー（概要、アプローチ、重要ポイント、結果、使用技術）
  - [x] 関連リンク抽出（Kaggle Notebooks、GitHub、その他）
  - [x] オンデマンド要約生成とキャッシング機能
  - [x] 専用詳細ページでの閲覧
- [ ] 全文検索機能
- [ ] トレンド分析
- [ ] フィルタリング機能（ステータス、カテゴリ、難易度など）

### Phase 3: 自動化・拡張
- [ ] 定期実行スケジューラー
- [ ] データセット情報収集
- [ ] ノートブック解法の収集（Notebookタイプの解法対応）
- [ ] CLI ツール

---

## 🔌 外部ツール連携

このプロジェクトでは、以下の外部ツールをMCP (Model Context Protocol) 経由で利用できます：

- **Kaggle MCP**: Kaggle API との直接連携（コンペ情報、データセット、ノートブック操作）
- **SQLite MCP**: 軽量データベース操作（開発・テスト用）
- **PostgreSQL MCP**: 本番用データベース操作（スキーマ設計、クエリ実行）
- **GitHub MCP**: リポジトリ操作、Issue/PR管理
- **Serena MCP**: 高度なコード分析・編集
- **Context7 MCP**: 最新ライブラリドキュメントの参照（Kaggle API、SQLAlchemy等）
- **Playwright MCP**: ブラウザ自動化、Webスクレイピング（Kaggle Web UI操作用）
- **Notion MCP**: 開発記録・メモの管理（オプション）

### MCP設定ファイル

- **`.mcp.json`**: MCPサーバーの設定（APIトークン含む、Gitから除外）
- **`.mcp.json.template`**: 設定のテンプレート
- **`.env.example`**: 環境変数のサンプル
- **`.claude/settings.local.json`**: Claude Code の設定

### 初回セットアップ

1. `.env.example` をコピーして `.env` を作成
2. `.env` に実際のAPIキーを記載
3. `.mcp.json` のPostgreSQL接続文字列を環境に合わせて修正
4. Claude Code を再起動してMCPサーバーを有効化

---

## 📖 参考情報

- **プロジェクト固有ルール**: [project_rules.md](./project_rules.md)
- **汎用開発ルール**: [general_rules.md](./general_rules.md)
- **全体仕様**: [docs/SPECIFICATION.md](../docs/SPECIFICATION.md)
- **API仕様**: [docs/api/](../docs/api/)

---

## 🔄 更新履歴

**2025-11-16**:
- Solutions機能の実装完了
  - 解法の自動識別とデータベース保存（`solutions`テーブル追加）
  - オンデマンドLLM要約生成（構造化JSON形式）
  - 関連リンク抽出（Kaggle Notebooks、GitHub、その他）
  - フロントエンドUI実装（SolutionCard、詳細ページ）
  - 要約のキャッシング機能（再スクレイピング不要）
- APIエンドポイント追加:
  - `POST /api/competitions/{id}/solutions/fetch` - 解法収集
  - `POST /api/solutions/{id}/summarize` - 要約生成

**2025-11-15**:
- プロジェクト開始
- Claude Code設定ファイルをKaggleツール用に整理
- ファイル構成（3分割）:
  - `CLAUDE.md` - プロジェクト概要とクイックリファレンス
  - `project_rules.md` - このプロジェクト固有のルール
  - `general_rules.md` - 汎用的な開発ルール

---

**最終更新**: 2025-11-16
