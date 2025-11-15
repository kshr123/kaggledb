# APIキーセットアップガイド

このガイドでは、Kaggle APIとOpenAI APIのキーを取得・設定する手順を説明します。

---

## 📝 必要なAPIキー

1. **Kaggle API** - コンペ情報の取得に使用
2. **OpenAI API** - LLM処理（要約・タグ生成）に使用

---

## 🔑 1. Kaggle APIキーの取得

### Step 1: Kaggleアカウントにログイン
https://www.kaggle.com にアクセスしてログイン

### Step 2: APIトークンを生成
1. 右上のプロフィールアイコン → **Settings** をクリック
2. **API** セクションまでスクロール
3. **Create New API Token** ボタンをクリック
4. `kaggle.json` ファイルが自動ダウンロードされます

### Step 3: kaggle.jsonを配置

**macOS / Linux:**
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Windows:**
```powershell
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\
```

### Step 4: kaggle.jsonの内容を確認
```bash
cat ~/.kaggle/kaggle.json
```

出力例:
```json
{
  "username": "your_username",
  "key": "abc123def456..."
}
```

### Step 5: backend/.env に設定
`backend/.env` ファイルを開いて、以下を記入：

```bash
KAGGLE_USERNAME=your_username
KAGGLE_KEY=abc123def456...
```

---

## 🤖 2. OpenAI APIキーの取得

### Step 1: OpenAIアカウントにログイン
https://platform.openai.com にアクセスしてログイン

### Step 2: APIキーを生成
1. 左メニューから **API keys** をクリック
2. **+ Create new secret key** ボタンをクリック
3. キー名を入力（例: `kaggle-kb-dev`）
4. **Create secret key** をクリック
5. 表示されたAPIキーをコピー（⚠️ 一度しか表示されません！）

### Step 3: backend/.env に設定
`backend/.env` ファイルを開いて、以下を記入：

```bash
OPENAI_API_KEY=sk-proj-...
```

---

## ✅ 3. 設定確認

### backend/.env の最終確認

`02_backend/.env` を開いて確認：

```bash
# Kaggle API 認証
KAGGLE_USERNAME=your_actual_username
KAGGLE_KEY=your_actual_api_key

# OpenAI API
OPENAI_API_KEY=sk-proj-your_actual_key

# Database
DATABASE_PATH=./data/kaggle_competitions.db

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### 動作確認（オプション）

**Kaggle API:**
```bash
kaggle competitions list
```

**OpenAI API:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 🔒 セキュリティ注意事項

### ✅ やるべきこと
- `.env` ファイルは絶対にGitにコミットしない（`.gitignore`で除外済み）
- APIキーは他人と共有しない
- 公開リポジトリにアップロードしない

### ⚠️ 万が一APIキーが漏洩した場合
- **Kaggle**: Settings → API → "Create New API Token" で再発行
- **OpenAI**: API keys → 該当キーを "Revoke" → 新しいキーを作成

---

## 💰 料金について

### Kaggle API
- **無料** - 制限なし

### OpenAI API
- **従量課金制** - GPT-4o miniは非常に安価
- 目安: コンペ100件の要約で約$0.10〜$0.20
- 料金確認: https://platform.openai.com/usage

---

## 🚀 次のステップ

環境変数の設定が完了したら、次の作業に進めます：

1. データベーススキーマ設計
2. データベース初期化スクリプト作成
3. FastAPI基盤構築

---

**最終更新**: 2025-11-15
