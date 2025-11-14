# テスト結果管理ルール

## 📝 基本方針

**すべてのテスト結果は証跡として保存する**

- TDDの Red → Green の過程を証明
- デバッグ時の参考資料
- コードレビュー時の根拠

---

## 📂 テスト結果の保存場所

### ディレクトリ構造
```
backend/
├── tests/                   # テストコード
│   ├── __init__.py
│   ├── test_init_db.py
│   ├── test_kaggle_client.py
│   ├── ...
│   └── test_results/       # テスト結果（生データ）
│       ├── test_results_init_db.txt
│       ├── test_results_kaggle_client.txt
│       └── ...
│
├── TEST_GUIDE.md           # テストガイド（汎用）
└── TEST_RESULTS_SUMMARY.md # テスト結果の見方（汎用）
```

### ファイルの役割

| ファイル | 役割 | Git管理 |
|---------|------|---------|
| `tests/test_*.py` | テストコード | ✅ 管理する |
| `tests/test_results/test_results_*.txt` | テスト結果（生データ） | ✅ 管理する |
| `tests/.pytest_cache/` | pytestキャッシュ | ❌ 除外する |
| `TEST_GUIDE.md` | テストガイド（汎用） | ✅ 管理する |
| `TEST_RESULTS_SUMMARY.md` | テスト結果の見方 | ✅ 管理する |

---

## 📋 テスト結果の保存ルール

### 1. 保存コマンド

```bash
# テスト実行 & 結果保存
pytest tests/test_xxx.py -v > tests/test_results/test_results_xxx.txt 2>&1
```

### 2. ファイル命名規則

```
test_results_[機能名].txt          # 通常（Greenフェーズ）
test_results_[機能名]_red.txt      # Redフェーズ（失敗確認時のみ）
test_results_[機能名]_YYYYMMDD.txt # 日時付き（履歴管理時）
```

**例:**
- `tests/test_results/test_results_init_db.txt` - データベース初期化テスト
- `tests/test_results/test_results_kaggle_client.txt` - Kaggle APIクライアントテスト
- `tests/test_results/test_results_init_db_red.txt` - Red フェーズの結果（失敗確認）

### 3. 保存タイミング

| フェーズ | 保存タイミング | ファイル名 |
|---------|---------------|-----------|
| **Red** | テスト作成後（失敗確認） | `_red.txt` |
| **Green** | 実装完了後（成功確認） | `.txt` |
| **Refactor** | リファクタリング後 | `.txt`（上書き） |

---

## 🔍 テスト結果の見方

### 出力形式の解説

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/kotaro/Desktop/dev/kaggledb/backend
plugins: cov-7.0.0
collecting ... collected 8 items

tests/test_init_db.py::TestDatabaseInitialization::test_create_competitions_table PASSED [ 12%]
tests/test_init_db.py::TestDatabaseInitialization::test_create_discussions_table PASSED [ 25%]
...

============================== 8 passed in 0.08s ===============================
```

### 読み方

| 部分 | 説明 |
|------|------|
| `platform darwin` | 実行環境（OS） |
| `Python 3.9.6` | Pythonバージョン |
| `pytest-8.4.2` | pytestバージョン |
| `collected 8 items` | 検出されたテスト数 |
| `PASSED` | テスト成功 ✅ |
| `FAILED` | テスト失敗 ❌ |
| `[ 12%]` | 進捗率 |
| `8 passed in 0.08s` | 結果サマリー |

---

## ✅ 良い例・悪い例

### 良い例 ✅

```bash
# テスト実行後、必ず結果を保存
pytest tests/test_init_db.py -v > tests/test_results/test_results_init_db.txt 2>&1
cat tests/test_results/test_results_init_db.txt  # 確認

# Redフェーズの記録も残す
pytest tests/test_new_feature.py -v > tests/test_results/test_results_new_feature_red.txt 2>&1
```

### 悪い例 ❌

```bash
# 結果を保存しない
pytest tests/test_init_db.py -v

# 標準エラー出力を捨てる
pytest tests/test_init_db.py -v > tests/test_results/test_results_init_db.txt

# ファイル名が不統一
pytest tests/test_init_db.py -v > init_db_test.txt
pytest tests/test_kaggle.py -v > result_kaggle_client.log
```

---

## 🚫 やってはいけないこと

1. **テスト結果を保存しない** - 証跡が残らない
2. **標準エラー出力を捨てる** - エラー情報が失われる
3. **ファイル名が不統一** - 管理が煩雑になる
4. **tests/test_results/をGit除外** - 証跡が失われる
5. **tests/.pytest_cache/をGit管理** - 不要なファイルがコミットされる

---

## 📊 TEST_GUIDE.md と TEST_RESULTS_SUMMARY.md の使い分け

### TEST_GUIDE.md（推奨）
- **役割**: テストの実行方法とガイド
- **内容**:
  - pytest実行コマンド
  - カバレッジ測定方法
  - トラブルシューティング
  - ベストプラクティス

### TEST_RESULTS_SUMMARY.md
- **役割**: テスト結果の見方（汎用）
- **内容**:
  - ステータス表示の説明
  - サマリーの読み方
  - tests/test_results/への参照

**実際のテスト結果は `tests/test_results/*.txt` に保存**

---

## 🔄 運用フロー

### 新機能実装時

```bash
# 1. テストを書く（Red）
vim tests/test_new_feature.py

# 2. テストを実行（失敗確認）
pytest tests/test_new_feature.py -v > tests/test_results/test_results_new_feature_red.txt 2>&1

# 3. 実装する（Green）
vim app/new_feature.py

# 4. テストを実行（成功確認）
pytest tests/test_new_feature.py -v > tests/test_results/test_results_new_feature.txt 2>&1

# 5. リファクタリング
vim app/new_feature.py

# 6. テスト再実行（成功確認）
pytest tests/test_new_feature.py -v > tests/test_results/test_results_new_feature.txt 2>&1
```

---

**作成日**: 2025-11-15
**最終更新**: 2025-11-15
