# テスト結果ガイド

このディレクトリには、pytestの実行結果が保存されています。

## 📋 ファイル命名規則

**形式**: `test_results_{テストモジュール名}.txt`

**例**:
- `test_results_config.txt` - 設定テスト (`tests/test_config.py`)
- `test_results_init_db.txt` - DB初期化テスト (`tests/test_init_db.py`)
- `test_results_init_db_updated.txt` - DB初期化テスト（更新版）

**バージョン管理**:
- 同じテストを複数回実行した場合、`_v2`, `_updated` などのサフィックスを追加
- 重要な変更の前後で結果を残すと比較に便利

---

## 📖 テスト結果の読み方

### ✅ 成功例
```
tests/test_init_db.py::TestDatabaseInitialization::test_create_tags_table PASSED [50%]
```

- **`PASSED`**: テスト成功
- **`[50%]`**: 進捗（全体の50%完了）
- **`test_create_tags_table`**: テスト関数名

### ❌ 失敗例
```
tests/test_init_db.py::TestDatabaseInitialization::test_insert_initial_tags FAILED [62%]

AssertionError: assert 20 == 60
  +  where 20 = <built-in method fetchone of sqlite3.Cursor object>()[0]
```

- **`FAILED`**: テスト失敗
- **`AssertionError`**: アサーションエラー（期待値と実際の値が異なる）
- **`assert 20 == 60`**: 期待値60に対して実際は20だった

### 📊 サマリ行の見方
```
============================== 8 passed in 0.07s ===============================
```

- **`8 passed`**: 8個のテストが成功
- **`in 0.07s`**: 実行時間0.07秒

```
========================= 1 failed, 7 passed in 0.10s ==========================
```

- **`1 failed, 7 passed`**: 1個失敗、7個成功

---

## 💻 テスト実行方法

### 全テスト実行
```bash
source .venv/bin/activate
pytest tests/ -v
```

### 特定のテストファイルのみ実行
```bash
pytest tests/test_init_db.py -v
```

### 特定のテストクラス/関数のみ実行
```bash
# クラス単位
pytest tests/test_init_db.py::TestDatabaseInitialization -v

# 関数単位
pytest tests/test_init_db.py::TestDatabaseInitialization::test_insert_initial_tags -v
```

### テスト結果を保存
```bash
pytest tests/test_init_db.py -v > tests/test_results/test_results_init_db.txt 2>&1
```

**重要**: `2>&1` を付けることでエラー出力も含めて保存されます。

### カバレッジレポート付きで実行
```bash
pytest tests/ --cov=app --cov-report=term -v
```

---

## 🔍 よくあるエラーと対処法

### 1. ModuleNotFoundError
```
ModuleNotFoundError: No module named 'app'
```

**原因**: 仮想環境がアクティブでない、またはパッケージ未インストール
**対処**:
```bash
source .venv/bin/activate
uv pip install -e .
```

### 2. ImportError
```
ImportError: cannot import name 'initialize_database' from 'app.batch.init_db'
```

**原因**:
- 実装がまだない（TDD Redフェーズ）
- ファイルパスが間違っている

**対処**:
- Redフェーズなら正常（これから実装）
- それ以外ならファイルパスとインポートを確認

### 3. AssertionError
```
AssertionError: assert 20 == 60
```

**原因**: 期待値と実際の値が異なる（仕様とコードの不一致）
**対処**:
- TDD Redフェーズなら正常（実装がまだ）
- Greenフェーズなら実装を修正

### 4. fixture not found
```
fixture 'temp_db' not found
```

**原因**: fixtureの定義がない、またはインポートされていない
**対処**: `conftest.py` または同じファイル内に `@pytest.fixture` を定義

---

## 📁 テスト結果ファイルの履歴

| ファイル名 | 実行日時 | 結果 | 説明 |
|-----------|---------|------|------|
| `test_results_config.txt` | 2025-11-15 14:30 | ✅ 7/7 passed | 設定テスト（環境変数、パス） |
| `test_results_init_db.txt` | 2025-11-15 14:45 | ✅ 8/8 passed | DB初期化テスト（旧スキーマ、20タグ） |
| `test_results_init_db_updated.txt` | 2025-11-15 15:30 | ✅ 8/8 passed | DB初期化テスト（新スキーマ、60タグ） |

**変更履歴**:
- `2025-11-15 15:30`: タグシステム拡張（20タグ → 60タグ、4カテゴリ → 6カテゴリ）

---

## 🔗 関連ドキュメント

- **全体仕様**: `01_docs/03_data_design.md`, `01_docs/07_api_design.md`
- **スキーマ定義**: `02_backend/schema.sql`
- **テストコード**: `02_backend/tests/`
- **実装コード**: `02_backend/app/`

---

## 📝 テスト結果ファイルの書き方（テンプレート）

新しいテスト結果を保存する際は、以下の形式でヘッダーを追加してください：

```txt
================================================================================
[テスト結果] {テスト名}
================================================================================
📅 実行日時: YYYY-MM-DD HH:MM:SS
📦 対象モジュール: {モジュール名} ({テストファイル名})
📋 テスト内容:
   - {テスト項目1}
   - {テスト項目2}

✅ 期待される結果: {期待結果}

🔗 関連仕様:
   - {仕様書ファイル}

📌 変更点（前回からの差分）:
   - {変更内容}

💻 実行コマンド:
   pytest {テストファイル} -v > tests/test_results/{結果ファイル} 2>&1

================================================================================

[pytest 出力]
============================= test session starts ==============================
...
```

---

## 🚀 ベストプラクティス

### 1. テスト結果は必ず保存する
- TDD の Red/Green フェーズの証拠になる
- 後から「なぜこのテストが失敗したのか」を振り返れる

### 2. 重要な変更の前後で保存する
- スキーマ変更前後
- 大きなリファクタリング前後
- バグフィックス前後

### 3. ヘッダーに文脈を書く
- 何をテストしたのか
- なぜこのテストを実行したのか
- 前回との差分は何か

### 4. 失敗したテスト結果も残す（Red フェーズ）
- TDD の Red フェーズの証拠
- 「テストファーストで開発した」ことが分かる

### 5. テスト結果ファイルは .gitignore に追加
- テスト結果自体は Git 管理しない（再生成可能）
- この README.md は Git 管理する（ドキュメントとして価値がある）

---

**最終更新**: 2025-11-15
