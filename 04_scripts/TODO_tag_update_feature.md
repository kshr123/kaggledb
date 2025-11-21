# タグ更新機能の実装TODO

## 目的
データセットやディスカッション情報を活用して、コンペティションのタグをより正確に更新できるようにする

## 背景
- 現在の実装では、Overview ページのテキストと評価指標のみでタグ付けしている
- 評価指標（F1-score など）に過度に依存しているため、誤検出がある
- 今後、データセット情報やディスカッション要約が追加された際に、より正確な判定が可能

## 実装内容

### 1. タグ更新スクリプト (`04_scripts/update_competition_tags.py`)

**機能**:
- 既存コンペのタグを再評価
- 追加情報（データセット、ディスカッション）を考慮した判定
- オプション指定で更新対象を制御

**コマンドライン引数**:
```bash
# 全件更新
python update_competition_tags.py --all

# 特定のコンペのみ
python update_competition_tags.py --comp-id=titanic

# 新規情報が追加されたコンペのみ（デフォルト）
python update_competition_tags.py

# ドライラン（実際には更新しない）
python update_competition_tags.py --dry-run
```

**更新判定ロジック**:
- `last_scraped_at` が `updated_at` より新しいコンペを対象
- または `--all` オプションで全件対象

### 2. プロンプト改善

**追加情報を考慮**:
```python
prompt = f"""
以下の情報からコンペティションのタグを選択してください。

# 基本情報
- タイトル: {title}
- ドメイン: {domain}
- 評価指標: {metric}

# 詳細説明（Overviewページ）
{full_text}

# データセット情報（利用可能な場合）
{dataset_info}

# ディスカッションからの知見（利用可能な場合）
{discussion_insights}

# タグ選択
以下の選択肢から該当するものをすべて選択してください。
**評価指標だけでなく、実際の課題やデータの特徴を重視してください。**

## competition_features
選択肢: ["不均衡データ", "欠損値多い", "外れ値対策必要", ...]

判定基準:
- **不均衡データ**:
  - データセット情報でクラス分布の偏りが確認できる
  - ディスカッションで不均衡対策が議論されている
  - テキストに "imbalance", "rare event", "fraud" などの記述
  - 評価指標（F1, Balanced Accuracy）は参考程度

...
"""
```

### 3. APIエンドポイント追加（オプション）

**バックエンド** (`02_backend/app/routers/competitions.py`):
```python
@router.post("/competitions/{competition_id}/tags/refresh")
def refresh_competition_tags(
    competition_id: str,
    service: Annotated[CompetitionService, Depends(get_competition_service)]
):
    """
    コンペティションのタグを再評価して更新

    Returns:
        dict: 更新前後のタグ情報
    """
    from app.services.tag_update_service import get_tag_update_service

    tag_service = get_tag_update_service()
    result = tag_service.refresh_tags(competition_id)

    return {
        "success": True,
        "competition_id": competition_id,
        "old_tags": result["old_tags"],
        "new_tags": result["new_tags"],
        "changes": result["changes"]
    }
```

**フロントエンド**:
- コンペ詳細ページに「タグを再評価」ボタンを追加
- クリックで API を呼び出し、タグを更新

### 4. 自動更新フロー（オプション）

**トリガー**:
- ディスカッション取得後
- データセット情報追加後
- 解法分析完了後

**実装**:
```python
# ディスカッション取得後に自動更新
@router.post("/competitions/{competition_id}/discussions/fetch")
def fetch_discussions(...):
    # ... ディスカッション取得処理 ...

    # オプション: タグも自動更新
    if auto_refresh_tags:
        tag_service.refresh_tags(competition_id)

    return result
```

## 実装優先度

### Phase 1（必須）
- [x] `competition_features` と `task_types` フィールド追加
- [x] 基本的なタグ付け機能
- [ ] タグ更新スクリプト (`update_competition_tags.py`)

### Phase 2（推奨）
- [ ] プロンプト改善（データセット情報考慮）
- [ ] ディスカッション要約を考慮したタグ付け

### Phase 3（オプション）
- [ ] APIエンドポイント追加
- [ ] フロントエンドUIの追加
- [ ] 自動更新フロー

## 参考

### 現在のタグ分布（93件時点）
- 不均衡データ: 50件（54%）← 評価指標に依存しすぎている可能性
- 大規模データ: 69件（74%）
- 欠損値多い: 22件（24%）

### 改善後の期待値
- より文脈を重視した判定
- 誤検出の削減（例: ARC Prizeの「不均衡データ」タグ除去）
- データセット情報による正確性向上
