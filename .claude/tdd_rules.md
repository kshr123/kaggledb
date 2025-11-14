# TDD（テスト駆動開発）ルール

## 🎯 基本原則

### Red → Green → Refactor サイクル

1. **Red（失敗するテストを書く）**
   - 実装する前にテストを書く
   - テストは必ず失敗することを確認

2. **Green（最小限の実装でテストを通す）**
   - テストをパスする最小限のコードを書く
   - 美しさより動作優先

3. **Refactor（リファクタリング）**
   - テストを保ったままコードを改善
   - 重複削除、可読性向上

---

## 📝 必須ルール

### ✅ テスト結果の記録

**すべてのテスト実行後、以下を必ず行うこと：**

1. **テスト結果をファイルに保存**
   ```bash
   pytest tests/test_xxx.py -v > test_results_xxx.txt 2>&1
   ```

2. **TEST_RESULTS_SUMMARY.md に記録**
   - テスト結果の全文をコピー
   - サマリー（総数、成功/失敗数、実行時間）を記載
   - テストカバレッジ表を作成
   - 検証内容を記載

3. **個別のテスト結果ファイルも保管**
   - `test_results_[機能名].txt` として保存
   - Git管理対象（`.gitignore`から除外しない）

### 理由
- **証拠**: Red→Greenの過程を証明
- **デバッグ**: 失敗時の調査に役立つ
- **ドキュメント**: 何をテストしたか明確
- **レビュー**: コードレビュー時の参考資料

---

## 📁 ファイル構成

```
backend/
├── tests/
│   ├── test_init_db.py           # テストコード
│   ├── test_kaggle_client.py
│   └── ...
├── test_results_init_db.txt      # テスト結果（個別）
├── test_results_kaggle_client.txt
├── ...
└── TEST_RESULTS_SUMMARY.md       # テスト結果サマリー（統合）
```

---

## 🔄 開発フロー（TDD）

### 新機能実装時

```bash
# 1. テストを書く（Red）
vim tests/test_new_feature.py

# 2. テストを実行（失敗することを確認）
pytest tests/test_new_feature.py -v

# 3. 実装する（Green）
vim app/new_feature.py

# 4. テストを実行（成功することを確認）
pytest tests/test_new_feature.py -v > test_results_new_feature.txt 2>&1

# 5. テスト結果を記録
# TEST_RESULTS_SUMMARY.md に追加
cat test_results_new_feature.txt  # 確認

# 6. リファクタリング（必要に応じて）
vim app/new_feature.py

# 7. テストが通ることを再確認
pytest tests/test_new_feature.py -v
```

---

## 🎯 テストの粒度

### 単体テスト（Unit Test）
- 1つの関数/メソッドをテスト
- 外部依存をモック化
- 高速（ミリ秒単位）

### 統合テスト（Integration Test）
- 複数のコンポーネントをテスト
- 実際のDB/APIを使用
- 中速（秒単位）

### E2Eテスト（End-to-End Test）
- システム全体をテスト
- ユーザー視点でのシナリオ
- 低速（分単位）

---

## 📊 テストカバレッジの目標

- **コアロジック**: 100%
- **APIエンドポイント**: 90%以上
- **ユーティリティ**: 80%以上
- **全体**: 80%以上

### カバレッジ確認
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 🚫 やってはいけないこと

1. **テストなしで実装** - TDDの原則に反する
2. **テスト結果を記録しない** - 証跡が残らない
3. **失敗するテストをコミット** - CIが壊れる
4. **テストをスキップ** - カバレッジが下がる
5. **実装に合わせてテストを変更** - テストの意味がない

---

## ✅ 良い例・悪い例

### 良い例 ✅
```python
# tests/test_calculator.py
def test_add_two_numbers():
    """2つの数値を正しく加算できるか"""
    result = add(2, 3)
    assert result == 5

def test_add_negative_numbers():
    """負の数も正しく加算できるか"""
    result = add(-1, -2)
    assert result == -3
```

### 悪い例 ❌
```python
# tests/test_calculator.py
def test_everything():
    """すべてをテスト"""
    assert add(2, 3) == 5
    assert subtract(5, 2) == 3
    assert multiply(2, 3) == 6
    # 1つのテストで複数の機能をテスト（分割すべき）
```

---

## 📚 参考資料

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [Test Driven Development: By Example（Kent Beck）](https://www.amazon.co.jp/dp/0321146530)

---

**作成日**: 2025-11-15
**最終更新**: 2025-11-15
