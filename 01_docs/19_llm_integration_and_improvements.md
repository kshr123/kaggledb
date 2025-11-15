# 19. LLM統合と改善（2025-11-16）

## 📋 概要

このドキュメントでは、LLMを活用したコンペティション情報の充実化機能と、評価指標・タグ表示の改善について記録します。

---

## 🎯 実装した機能

### 1. LLMサービスの実装

**ファイル**: `02_backend/app/services/llm_service.py`

OpenAI GPT-4oを使用して、以下の機能を提供：

#### 1.1 構造化要約生成 (`generate_summary`)

コンペティションの英語説明文から、5つのフィールドを持つ構造化された日本語要約を生成：

```json
{
  "overview": "コンペの概要（1-2文、50-100文字）",
  "objective": "何を予測/分類するか（30-50文字）",
  "data": "使用するデータの種類（30-50文字）",
  "business_value": "ビジネス上の価値・目的（50-80文字）",
  "key_challenges": ["課題1", "課題2", "課題3"]
}
```

**特徴**:
- JSON形式で構造化された出力
- 各フィールドに文字数制限を設定
- リトライ機能（最大3回）

#### 1.2 タグ自動生成 (`generate_tags`)

説明文から以下のタグを自動生成：

- **data_types**: データの種類（画像、テキスト、時系列など）
- **tags**: タスクタイプ、コンペ特徴
- **domain**: ドメイン（医療、金融、コンピュータビジョンなど）

**重要なルール**:
- **推測は一切禁止**: 説明文に明示されている情報のみ選択
- **task_type の厳密な基準**:
  - 「分類」: "classify", "classification", "identify", "recognize"
  - 「回帰」: "predict" + 連続値
  - 「物体検出」: "object detection", "detect objects", "bounding box", "localization"
  - 「セグメンテーション」: "segment", "segmentation", "pixel-level"
  - ⚠️ **"detect behaviors", "detect patterns" は「分類」として扱う**（物体検出ではない）

#### 1.3 評価指標抽出 (`extract_evaluation_metric`)

説明文から評価指標を抽出（実装済みだが、APIの `description` が短すぎるため現在は使用していない）

**将来の改善**: Webスクレイピングで詳細情報を取得する際に活用予定

---

### 2. 評価指標の表示改善

#### 2.1 Kaggle APIバグ修正

**問題**: `kaggle_client.py` で `evaluationMetric` (キャメルケース) を参照していたが、実際のAPIは `evaluation_metric` (スネークケース) を返していた

**修正**: `02_backend/app/services/kaggle_client.py:107`
```python
# 修正前
metric = getattr(comp, 'evaluationMetric', 'Unknown')

# 修正後
metric = getattr(comp, 'evaluation_metric', 'Unknown')
```

#### 2.2 内部コード名のフィルタリング

**問題**: カスタム指標を使用するコンペで、APIが内部コード名を返す
- 例: "NFL_2025", "cafa6_metric_final"

**解決策**: フロントエンドで内部コード名を非表示にする

**実装**: `03_frontend/app/page.tsx:330-343`
```typescript
function isDisplayableMetric(metric: string): boolean {
  if (!metric) return false

  const hasSpace = / /.test(metric)
  const hasUnderscore = /_/.test(metric)

  // アンダースコアを含み、スペースがない場合は内部コード名
  if (hasUnderscore && !hasSpace) {
    return false
  }

  return true
}
```

**判定基準**:
- ❌ 非表示: "nfl_2025", "cafa6_metric_final", "NFL_2025"（アンダースコア + スペースなし）
- ✅ 表示: "Hull Competition Sharpe", "MABe F Beta", "R2 Score"（スペースを含む）

---

### 3. UIの情報優先度改善

**ファイル**: `03_frontend/app/page.tsx`

コンペティション一覧で、重要な情報を優先的に表示：

**表示順序**:
1. **ステータス** (🟢 開催中 / 🔴 終了済み)
2. **評価指標** (📊 Hull Competition Sharpe)
3. **タスクタイプ** (🎯 分類（多クラス）)
4. **構造化要約** (overview, objective, data, business_value, key_challenges)
5. **補助情報** (🏷️ ドメイン、📅 終了日)
6. **その他のタグ** (タスクタイプ以外)

---

## 🛠️ 実装したスクリプト

### 1. `enrich_competitions.py`

既存のコンペティション情報に要約とタグを生成・追加

```bash
# 全コンペ処理
python enrich_competitions.py

# 3件のみテスト
python enrich_competitions.py --limit 3

# Dry run（更新なし）
python enrich_competitions.py --dry-run
```

### 2. `update_metrics.py`

Kaggle APIから評価指標を再取得してデータベースを更新

```bash
python update_metrics.py
```

### 3. `extract_metrics_from_description.py`

説明文から評価指標を抽出（将来のWebスクレイピング実装時に使用予定）

```bash
python extract_metrics_from_description.py --dry-run
```

### 4. `fix_mabe.py`

特定のコンペティション（MABe）のタグを修正

---

## 📊 データベース変更

### 変更なし

既存のスキーマを維持：
- `summary`: 構造化要約のJSON文字列
- `tags`: タグの配列（JSON）
- `data_types`: データタイプの配列（JSON）
- `domain`: ドメイン文字列
- `metric`: 評価指標名

---

## 🔄 処理フロー

### コンペティション情報充実化フロー

```
1. Kaggle APIからコンペ基本情報を取得
   ↓
2. LLMで構造化要約を生成
   ↓
3. LLMでタグを生成（推測禁止）
   ↓
4. データベースに保存
   ↓
5. フロントエンドで表示
   - 評価指標: 内部コード名はフィルタリング
   - タグ: タスクタイプを優先表示
   - 要約: 構造化されたフォーマットで表示
```

---

## 🎨 UI/UX改善

### 構造化要約の表示

**従来**: 長いテキストが読みにくい

**改善後**: 構造化されたフォーマット

```
Overview: コンペの概要を1-2文で

予測対象: タンパク質の生物学的機能を予測
データ: タンパク質のアミノ酸配列データ

価値: 新薬開発や疾患研究におけるタンパク質機能の理解を促進

主な課題:
• タンパク質の多様性と複雑性
• 機能アノテーションの不足
• 高次元データの処理
```

---

## ⚠️ 既知の制限事項

### 1. 評価指標の詳細情報

**問題**: Kaggle APIの `description` は1文程度で、評価指標の詳細が含まれていない

**現状の対応**: 内部コード名は非表示

**将来の改善**: Webスクレイピングで詳細情報を取得（ディスカッション情報取得機能と併せて実装予定）

### 2. タグ生成の精度

**問題**: 短い説明文からのタグ生成は制約が多い

**対策**:
- 推測を禁止し、明示的な情報のみ使用
- 不確実な場合は空配列/空文字列を返す

---

## 🚀 今後の改善予定

### 1. Webスクレイピング機能

- Kaggle コンペティションページから詳細情報を取得
- 評価指標の詳細説明
- ディスカッション情報
- より詳しいコンペ説明

### 2. タグの精度向上

- より多くのコンペデータで学習
- ユーザーフィードバックによる改善

### 3. 要約の品質向上

- ユーザーフィードバック
- プロンプトの最適化

---

## 🎨 UI/UXの最終決定

### Design 3: ダッシュボードスタイルを採用

3つのデザイン案を比較検討した結果、**Design 3（ダッシュボードスタイル）** を採用。

**採用理由**:
- データビジュアライゼーション重視
- プロフェッショナルな外観
- ヘッダー統計バーで重要指標を常時表示
- 視覚的な階層構造が明確

**主な特徴**:
- ヘッダー統計バー（総コンペ数、開催中、終了済みをリアルタイム表示）
- グラデーションバッジとアクセントカラー（青・緑）
- ホバー時の青いアクセントバー
- アニメーション付きパルス効果（開催中ステータス）
- プロフェッショナルなシャドウとボーダー効果

---

## 📝 変更履歴

| 日付 | 変更内容 | 担当 |
|------|----------|------|
| 2025-11-16 | LLMサービス実装、評価指標表示改善、タグ生成改善 | Claude Code |
| 2025-11-16 | 構造化要約フォーマット実装 | Claude Code |
| 2025-11-16 | 内部コード名フィルタリング実装 | Claude Code |
| 2025-11-16 | UIデザイン3案実装、Design 3（ダッシュボードスタイル）採用 | Claude Code |

---

## 🔗 関連ドキュメント

- [02_requirements.md](./02_requirements.md) - 要件定義
- [07_api_design.md](./07_api_design.md) - API設計
- [10_frontend_spec.md](./10_frontend_spec.md) - フロントエンド仕様
- [11_backend_spec.md](./11_backend_spec.md) - バックエンド仕様

---

**作成日**: 2025-11-16
**最終更新**: 2025-11-16
