# 評価指標マスターデータ管理ガイド

## 概要

このプロジェクトでは、Kaggleコンペの評価指標をフロントエンドで分類してフィルタリングできるようにしています。
新しいコンペデータを追加した際に、未分類の評価指標が発生する可能性があるため、定期的なチェックが必要です。

## マスターデータの場所

評価指標のマスターデータ（METRIC_GROUPS）は以下の2箇所に定義されています:

1. **フロントエンド**: `03_frontend/app/page.tsx` (11-38行目)
2. **チェックスクリプト**: `04_scripts/check_missing_metrics.py` (12-42行目)

**重要**: 両方のファイルを同期させる必要があります。

## 定期チェックフロー

### 1. 新しいコンペデータを追加した後

```bash
# スクリプトを実行
python 04_scripts/check_missing_metrics.py
```

### 2. 出力の確認

✅ **すべて分類済みの場合**:
```
✅ すべての評価指標が分類されています！
```
→ 何もする必要はありません。

⚠️ **未分類の指標がある場合**:
```
⚠️  未分類の評価指標が見つかりました:
  - New Metric Name                                  (5件)
```
→ 次のステップに進んでください。

### 3. 未分類指標の追加方法

#### Step 1: 適切なカテゴリを判断

新しい指標がどのカテゴリに属するか判断します:

- **分類タスク**: AUC系、F-Score系、Log Loss系、Accuracy系、その他
- **回帰タスク**: RMSE系、MAE系、相関系、その他
- **ランキングタスク**: MAP系、その他
- **その他**: カスタム、距離・誤差系、文字列類似度、確率・統計、画像・構造評価、ゲーム・シミュレーション、その他カスタム

#### Step 2: フロントエンドに追加

`03_frontend/app/page.tsx` の `METRIC_GROUPS` に追加:

```typescript
const METRIC_GROUPS = {
  '分類': {
    'AUC系': ['ROC AUC', 'PR-AUC', 'AUC', 'pAUC', 'New Metric Name'],  // 追加
    // ...
  },
  // ...
} as const
```

#### Step 3: チェックスクリプトに追加

`04_scripts/check_missing_metrics.py` の `METRIC_GROUPS` にも同じ内容を追加:

```python
METRIC_GROUPS = {
    '分類': {
        'AUC系': ['ROC AUC', 'PR-AUC', 'AUC', 'pAUC', 'New Metric Name'],  # 追加
        # ...
    },
    # ...
}
```

#### Step 4: 再チェック

```bash
python 04_scripts/check_missing_metrics.py
```

すべて分類されていれば完了です。

### 4. カテゴリ判断が難しい場合

以下のカテゴリに追加してください:

- **分類/その他**: 分類タスクだがどの系統にも属さない
- **回帰/その他**: 回帰タスクだがどの系統にも属さない
- **ランキング/その他**: ランキングタスクだがMAP系以外
- **その他/その他カスタム**: どのタスクにも属さない独自の指標

## CI/CDへの組み込み（推奨）

将来的に、以下のタイミングで自動チェックを実行することを推奨します:

1. **データ追加スクリプト実行後**:
   ```bash
   python 04_scripts/enrich_competitions.py
   python 04_scripts/check_missing_metrics.py
   ```

2. **GitHub Actions** (例):
   ```yaml
   - name: Check Missing Metrics
     run: python 04_scripts/check_missing_metrics.py
   ```

## トラブルシューティング

### 「余剰の指標」と表示される

マスターデータには定義されているが、現在のデータベースには存在しない指標です。
将来的に使用される可能性があるため、削除する必要はありません。

### スクリプトがエラーで終了する

未分類の指標がある場合、スクリプトは `exit code 1` で終了します。
これは CI/CD で異常を検出するためです。すべて分類されていれば `exit code 0` で正常終了します。

## 参考情報

- 評価指標の詳細: `03_frontend/app/page.tsx` の `METRIC_DESCRIPTIONS`
- データベーススキーマ: `02_backend/schema.sql`
- コンペ取得スクリプト: `04_scripts/fetch_competitions.py`
