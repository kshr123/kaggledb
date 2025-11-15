# 17. ドキュメント作成ガイドライン

## 📋 個人情報の取り扱い

### ❌ 禁止事項

**絶対にドキュメントに含めてはいけない情報**:

1. **個人のパス情報**
   ```bash
   # ❌ NG
   /Users/kotaro/Desktop/dev/kaggledb/backend/.env
   /home/username/projects/kaggledb
   C:\Users\YourName\Documents\kaggledb

   # ✅ OK
   02_backend/.env
   ./backend/.env
   /path/to/kaggledb/02_backend
   ```

2. **個人のユーザー名**
   ```bash
   # ❌ NG
   rootdir: /Users/kotaro/Desktop/dev/kaggledb/backend

   # ✅ OK
   rootdir: /path/to/kaggledb/02_backend
   ```

3. **実際のAPIキー・トークン**
   ```bash
   # ❌ NG
   KAGGLE_KEY=abc123def456ghi789...
   OPENAI_API_KEY=sk-proj-abc123...

   # ✅ OK
   KAGGLE_KEY=your_actual_api_key
   OPENAI_API_KEY=sk-proj-your_actual_key
   ```

4. **メールアドレス**
   ```bash
   # ❌ NG
   git config user.email "kotaro@example.com"

   # ✅ OK
   git config user.email "your_email@example.com"
   ```

---

## 📁 パス表記の標準

### プロジェクトルートからの相対パス

プロジェクト内のファイル・ディレクトリは**必ずプロジェクトルートからの相対パス**で記載：

```bash
# ✅ 推奨（プロジェクトルートからの相対パス）
01_docs/
02_backend/
03_frontend/
04_scripts/

02_backend/app/main.py
03_frontend/app/page.tsx
04_scripts/fetch_competitions.py
```

### 汎用的な絶対パス表記

どうしても絶対パスが必要な場合は、汎用的なプレースホルダーを使用：

```bash
# ✅ OK
/path/to/kaggledb/02_backend
/your/project/root/kaggledb
$PROJECT_ROOT/02_backend
```

### ホームディレクトリの表記

```bash
# ✅ OK
~/.kaggle/kaggle.json
$HOME/.kaggle/kaggle.json
%USERPROFILE%\.kaggle\kaggle.json  # Windows
```

---

## 📝 コードサンプルの書き方

### 環境変数の例

```bash
# ✅ Good
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_actual_api_key
DATABASE_PATH=./data/kaggle_competitions.db

# ❌ Bad
KAGGLE_USERNAME=kotaro123
KAGGLE_KEY=abc123def456...
```

### テスト結果の記載

```bash
# ✅ Good
rootdir: /path/to/kaggledb/02_backend
# または
rootdir: <project_root>/02_backend

# ❌ Bad
rootdir: /Users/kotaro/Desktop/dev/kaggledb/backend
```

### URLの例

```bash
# ✅ Good
http://localhost:3000
http://your-domain.com
https://api.example.com

# ❌ Bad（実際の本番URLやIPアドレス）
http://192.168.1.100:3000
http://kaggledb-prod.mycompany.internal
```

---

## ✅ ドキュメント公開前チェックリスト

ドキュメントをコミット・公開する前に確認：

- [ ] 個人のユーザー名が含まれていないか
- [ ] 個人のパス（`/Users/xxx`, `/home/xxx`, `C:\Users\xxx`）が含まれていないか
- [ ] 実際のAPIキー・トークンが含まれていないか
- [ ] 実際のメールアドレスが含まれていないか
- [ ] 実際の本番環境のURL・IPアドレスが含まれていないか
- [ ] サンプルコードの変数名が汎用的か（`your_username`, `example.com`など）

---

## 🔍 既存ドキュメントの確認方法

個人情報が含まれていないか確認：

```bash
# ユーザー名の検索
grep -r "kotaro" 01_docs/ 02_backend/ 03_frontend/ --include="*.md"

# 個人パスの検索
grep -r "/Users/" 01_docs/ 02_backend/ 03_frontend/ --include="*.md"
grep -r "/home/" 01_docs/ 02_backend/ 03_frontend/ --include="*.md"
grep -r "C:\\Users" 01_docs/ 02_backend/ 03_frontend/ --include="*.md"

# APIキーらしき文字列の検索
grep -rE "sk-[a-zA-Z0-9]{20,}" 01_docs/ --include="*.md"
grep -rE "[a-z0-9]{32,}" 01_docs/ --include="*.md"
```

---

## 📚 ドキュメント構成の標準

### 1. ファイル名

- **英数字とハイフン**のみ使用
- **小文字**推奨
- **連番接頭辞**を付与（例: `01_overview.md`, `02_requirements.md`）

### 2. 見出し構造

```markdown
# タイトル（H1）は1つのみ

## メインセクション（H2）

### サブセクション（H3）

#### 詳細項目（H4）
```

### 3. コードブロック

言語を必ず指定：

````markdown
```bash
npm install
```

```typescript
const data = await fetch('/api/competitions');
```

```python
def fetch_competitions(limit: int = 20):
    ...
```
````

### 4. 更新履歴

ドキュメント末尾に記載：

```markdown
---

**作成日**: YYYY-MM-DD
**最終更新**: YYYY-MM-DD
**作成者**: プロジェクト名
```

---

## 🚨 違反時の対応

個人情報がコミットされてしまった場合：

1. **即座に削除**:
   ```bash
   # 最新コミットから削除
   git reset --soft HEAD~1
   # 修正してから再コミット
   ```

2. **既にプッシュ済みの場合**:
   ```bash
   # ⚠️ 注意: 履歴を書き換えるため慎重に
   git revert <commit_hash>
   # または
   git filter-branch --tree-filter 'sed -i "s/kotaro/username/g" **/*.md'
   ```

3. **APIキーが漏洩した場合**:
   - 該当のAPIキーを**即座に無効化**
   - 新しいキーを発行
   - `.gitignore`で`.env`が除外されているか確認

---

**関連ドキュメント:**
- [セキュリティガイド](./08_non_functional_requirements.md)
- [APIセットアップガイド](./00_api_setup_guide.md)

---

**作成日**: 2025-11-15
**最終更新**: 2025-11-15
