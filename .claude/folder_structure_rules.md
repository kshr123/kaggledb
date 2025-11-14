# フォルダ構成ルール

## 📁 プロジェクトルートのフォルダ構成

### 基本方針
- **すべての主要フォルダに意味的な順序で連番を付ける（01-99）**
- **連番は開発・利用の順序を表す（仕様→実装→ツール→管理）**
- **隠しフォルダ（.で始まる）とNext.js標準フォルダ（public等）は例外**

---

## 🗂️ フォルダ構成（Kaggle Knowledge Base）

```
kaggledb/
├── .claude/              # Claude Code設定（隠しフォルダ）
├── .git/                 # Git管理（自動生成）
├── .gitignore
├── .env.local.example    # フロントエンド環境変数サンプル
├── .mcp.json             # MCP設定
│
├── 01_docs/              # ドキュメント（仕様書、API設計書等）
├── 02_backend/           # バックエンド（FastAPI）
├── 03_frontend/          # フロントエンド（Next.js App Router）
├── public/               # 静的ファイル（Next.js標準、連番なし）
├── 04_scripts/           # ユーティリティスクリプト
├── 05_progress/          # 進捗管理
│
├── package.json          # Next.js依存関係
├── tsconfig.json         # TypeScript設定
├── next.config.js        # Next.js設定
├── tailwind.config.ts    # Tailwind CSS設定
└── README.md             # プロジェクト全体のREADME
```

### フォルダの役割

| フォルダ | 役割 | 連番 | 理由 |
|---------|------|------|------|
| `.claude/` | Claude Code設定 | なし | 隠しフォルダ |
| `01_docs/` | ドキュメント・仕様書 | 01 | 最初に読むもの |
| `02_backend/` | FastAPIバックエンド | 02 | 実装の起点 |
| `03_frontend/` | Next.jsフロントエンド | 03 | バックエンドの次 |
| `public/` | 静的ファイル | なし | Next.js標準 |
| `04_scripts/` | スクリプト集 | 04 | ユーティリティ |
| `05_progress/` | 進捗管理 | 05 | 最後に見るもの |

---

## 📂 バックエンドフォルダ構成

```
02_backend/
├── .env                 # 環境変数（Git除外）
├── .env.example         # 環境変数サンプル
├── .venv/               # 仮想環境（Git除外）
├── requirements.txt     # Python依存関係
├── schema.sql           # データベーススキーマ
├── TEST_GUIDE.md        # テストガイド（汎用）
│
├── app/                 # アプリケーションコード
│   ├── __init__.py
│   ├── main.py          # FastAPIエントリポイント
│   ├── config.py        # 設定
│   ├── database.py      # DB接続
│   ├── models.py        # Pydanticモデル
│   │
│   ├── routers/         # APIルーター
│   │   ├── __init__.py
│   │   ├── competitions.py
│   │   ├── discussions.py
│   │   └── ...
│   │
│   ├── services/        # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── kaggle_client.py
│   │   ├── llm_client.py
│   │   └── ...
│   │
│   └── batch/           # バッチ処理
│       ├── __init__.py
│       ├── init_db.py
│       ├── fetch_competitions.py
│       └── ...
│
├── tests/               # テストコード
│   ├── __init__.py
│   ├── test_init_db.py
│   ├── test_kaggle_client.py
│   ├── ...
│   └── test_results/    # テスト結果（生データ）
│       ├── test_results_init_db.txt
│       ├── test_results_kaggle_client.txt
│       └── ...
│
└── data/                # データベースファイル（Git除外）
    └── kaggle_competitions.db
```

---

## 📋 テスト結果の管理ルール

### 保存場所
- **テスト結果**: `02_backend/tests/test_results/test_results_[機能名].txt`
- **pytestキャッシュ**: `02_backend/tests/.pytest_cache/`（自動生成、Git除外）

### ファイル命名規則
```
test_results_[機能名].txt          # 通常（Greenフェーズ）
test_results_[機能名]_red.txt      # Redフェーズ（失敗確認時のみ）
test_results_[機能名]_YYYYMMDD.txt # 日時付き（履歴管理時）
```

### Git管理
- ✅ **管理する**: `tests/test_results/*.txt`（証跡として重要）
- ❌ **除外する**: `tests/.pytest_cache/`（自動生成）

### 保存コマンド
```bash
# テスト実行 & 結果保存
pytest tests/test_xxx.py -v > tests/test_results/test_results_xxx.txt 2>&1
```

---

## 🚫 削除したフォルダ・ファイル

### 削除済み
- ~~`02_templates/`~~ - テンプレートフォルダ（未使用）
- ~~`.env.example`（ルート）~~ - `02_backend/.env.example`と重複

### 削除判断基準
- **3ヶ月以上使用していない**
- **プロジェクト仕様に含まれていない**
- **代替手段がある**

---

## 🔄 フォルダ名変更の履歴

| 変更日 | 変更前 | 変更後 | 理由 |
|--------|--------|--------|------|
| 2025-11-15 | `docs/` | `01_docs/` | 意味順連番（最初に読む） |
| 2025-11-15 | `backend/` | `02_backend/` | 意味順連番（実装の起点） |
| 2025-11-15 | `src/` | `03_frontend/` | 意味順連番+わかりやすい名前 |
| 2025-11-15 | `scripts/` | `04_scripts/` | 意味順連番（ユーティリティ） |
| 2025-11-15 | `progress/` | `05_progress/` | 意味順連番（最後に見る） |
| 2025-11-15 | `.env.example`（ルート） | 削除 | 02_backend/.env.exampleと重複 |
| 2025-11-15 | `02_templates/` | 削除 | 未使用のため |

---

## 📝 新規フォルダ追加時のルール

### 連番を付ける場合
- **すべての主要フォルダ**に意味的な順序で連番を付ける
- **意味的な順序**：仕様・ドキュメント → 実装 → ツール → 管理
- **01-99**の範囲で使用
- **例**: `06_monitoring/` (新規追加時)

### 連番を付けない場合
- **隠しフォルダ**（.で始まるフォルダ：`.claude/`, `.git/`等）
- **フレームワーク標準フォルダ**（Next.jsの`public/`, `node_modules/`等）
- **自動生成フォルダ**（`.venv/`, `.pytest_cache/`等）

### 意味的な順序の例
1. `01-09`: ドキュメント・仕様
2. `10-19`: コア実装
3. `20-29`: インフラ・ツール
4. `30-39`: テスト・品質管理（将来用）
5. `90-99`: 進捗・メモ・一時フォルダ

---

**最終更新**: 2025-11-15
