# テスト実行ガイド（汎用版）

> **注意**: テスト結果の生データは `tests/test_results/` フォルダに保存されています。
> このファイルは汎用的なテストの見方とガイドを記載しています。
> 詳細は `TEST_GUIDE.md` を参照してください。

---

## 📋 テスト結果の見方

### ステータス表示
- **PASSED** ✅ - テスト成功
- **FAILED** ❌ - テスト失敗
- **SKIPPED** ⏭️ - テストスキップ
- **ERROR** 💥 - テスト実行エラー

### 表示形式
```
tests/test_example.py::TestClass::test_method PASSED [ 50%]
                                               ^^^^^^   ^^^^
                                               ステータス 進捗率
```

---

## 1. データベース初期化（init_db.py）

### 実装日: 2025-11-15

### テスト結果
```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/kotaro/Desktop/dev/kaggledb/backend
plugins: cov-7.0.0
collecting ... collected 8 items

tests/test_init_db.py::TestDatabaseInitialization::test_create_competitions_table PASSED [ 12%]
tests/test_init_db.py::TestDatabaseInitialization::test_create_discussions_table PASSED [ 25%]
tests/test_init_db.py::TestDatabaseInitialization::test_create_solutions_table PASSED [ 37%]
tests/test_init_db.py::TestDatabaseInitialization::test_create_tags_table PASSED [ 50%]
tests/test_init_db.py::TestDatabaseInitialization::test_insert_initial_tags PASSED [ 62%]
tests/test_init_db.py::TestDatabaseInitialization::test_create_indexes PASSED [ 75%]
tests/test_init_db.py::TestDatabaseInitialization::test_idempotent_initialization PASSED [ 87%]
tests/test_init_db.py::TestDatabaseInitialization::test_foreign_key_constraints PASSED [100%]

============================== 8 passed in 0.08s ===============================
```

### サマリー
- **テスト総数**: 8
- **成功**: 8 ✅
- **失敗**: 0
- **実行時間**: 0.08秒

### テストカバレッジ
| テスト項目 | 内容 | 結果 |
|-----------|------|------|
| test_create_competitions_table | competitionsテーブル作成 | ✅ |
| test_create_discussions_table | discussionsテーブル作成 | ✅ |
| test_create_solutions_table | solutionsテーブル作成 | ✅ |
| test_create_tags_table | tagsテーブル作成 | ✅ |
| test_insert_initial_tags | 初期タグデータ挿入（20件） | ✅ |
| test_create_indexes | インデックス作成（9個） | ✅ |
| test_idempotent_initialization | 冪等性確認（複数回実行可能） | ✅ |
| test_foreign_key_constraints | 外部キー制約確認 | ✅ |

### データベース初期化結果
```
✅ Database initialized successfully: ./data/kaggle_competitions.db
   - Tables created: 4
   - Initial tags: 20
   - Indexes created: 9
```

### 検証内容
```sql
-- テーブル一覧
competitions  discussions   solutions     tags

-- タグ分類
データ系      : 5件
ドメイン系    : 5件
手法系        : 5件
課題系        : 5件
```

---

## 📝 次回のテスト結果追加方法

新しいテストを実行したら、このファイルに以下の形式で追加してください：

```markdown
## N. [機能名]（[ファイル名]）

### 実装日: YYYY-MM-DD

### テスト結果
[pytest出力をそのままコピー]

### サマリー
- **テスト総数**: X
- **成功**: X ✅
- **失敗**: X ❌
- **実行時間**: X秒

### テストカバレッジ
[各テストの説明]

### 検証内容
[動作確認の結果]
```

---

**最終更新**: 2025-11-15
