#!/usr/bin/env python3
"""
コンペ詳細情報の取得・整理スクリプト

詳細ページをスクレイピング → LLMで日本語に整理・構造化 → DB保存
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
import json
from datetime import datetime, date
from typing import Optional, Dict, Any
from app.services.scraper_service import get_scraper_service
from app.services.llm_service import get_llm_service
from app.config import DATABASE_PATH


def enrich_competition(
    comp_id: str,
    scraper,
    llm_service
) -> Optional[Dict[str, Any]]:
    """
    コンペ詳細を取得してLLMで構造化

    Returns:
        構造化されたコンペ情報（日本語）
    """
    print(f"\n{'='*60}")
    print(f"処理中: {comp_id}")
    print('='*60)

    # Step 1: 詳細ページをスクレイピング
    print("[1/3] 詳細ページをスクレイピング中...")
    scraped_data = scraper.get_tab_content(comp_id, tab="", force_refresh=False)

    if not scraped_data:
        print(f"❌ スクレイピング失敗: {comp_id}")
        return None

    full_text = scraped_data.get('full_text', '')
    if not full_text:
        print(f"❌ テキスト取得失敗: {comp_id}")
        return None

    print(f"✅ テキスト取得: {len(full_text)} 文字")

    # Step 2: LLMで構造化
    print("[2/3] LLMで日本語に整理・構造化中...")

    prompt = f"""
以下はKaggleコンペティションの詳細ページから取得したテキストです。
このテキストから必要な情報を抽出し、日本語で整理してJSON形式で返してください。

# 抽出する情報

1. **start_date**: 開始日（YYYY-MM-DD形式、不明な場合はnull）
2. **end_date**: 終了日（YYYY-MM-DD形式、不明な場合はnull）
3. **status**: "active"（開催中）または "completed"（終了）
4. **metric**: 評価指標名（例: "AUC", "RMSE", "Accuracy"）
5. **metric_description**: 評価指標の説明（日本語、100文字程度）
6. **summary**: コンペの内容を日本語で要約（200-300文字）
7. **domain**: ドメイン（例: "医療", "金融", "自然言語処理", "コンピュータビジョン"など）
8. **dataset_info**: データセットの概要（日本語、100文字程度、サイズやファイル形式など）

## タグ選択（以下の選択肢から該当するものを選んでください）

9. **competition_features**: コンペの特徴（該当するものすべて選択、該当なしなら空配列）
   選択肢: ["不均衡データ", "欠損値多い", "外れ値対策必要", "大規模データ", "小規模データ", "リーク対策必要", "時系列考慮", "ドメイン知識重要", "データ品質課題"]

10. **data_types**: データタイプ（該当するものすべて選択、最低1つ）
    選択肢: ["テーブルデータ", "画像", "テキスト", "時系列", "音声", "動画", "マルチモーダル"]

11. **task_types**: タスクタイプ（該当するものすべて選択、最低1つ）
    選択肢: ["分類（二値）", "分類（多クラス）", "回帰", "ランキング", "物体検出", "セグメンテーション", "生成", "クラスタリング", "レコメンド"]

# 判定のヒント

- **不均衡データ**: クラス分布の偏り、imbalance、rare event、fraud detection などの記述
- **欠損値多い**: missing values、NA、欠損値処理 などの記述
- **時系列考慮**: time series、temporal、順序を考慮 などの記述
- **レコメンド**: recommendation、推薦、suggest などの記述
- **評価指標**: AUC → 二値分類、F1-score → 不均衡データ、RMSE → 回帰

# 出力形式
必ずJSON形式で出力してください。他のテキストは含めないでください。

```json
{{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "status": "completed",
  "metric": "AUC",
  "metric_description": "ROC曲線下面積。0.5が完全にランダム、1.0が完璧な分類を示す。",
  "summary": "このコンペティションは...",
  "domain": "医療",
  "dataset_info": "約10,000枚のX線画像とメタデータCSV。合計サイズ約50GB。",
  "competition_features": ["不均衡データ", "大規模データ"],
  "data_types": ["画像", "テーブルデータ"],
  "task_types": ["分類（二値）"]
}}
```

# テキスト
{full_text[:15000]}
"""

    try:
        response = llm_service.generate(prompt)

        # JSONを抽出（```json ... ``` の中身を取得）
        if '```json' in response:
            json_start = response.find('```json') + 7
            json_end = response.find('```', json_start)
            json_str = response[json_start:json_end].strip()
        elif '```' in response:
            json_start = response.find('```') + 3
            json_end = response.find('```', json_start)
            json_str = response[json_start:json_end].strip()
        else:
            json_str = response.strip()

        enriched_data = json.loads(json_str)
        print(f"✅ LLM処理完了")
        print(f"   - summary: {enriched_data.get('summary', '')[:50]}...")
        print(f"   - tags: {enriched_data.get('tags', [])}")
        print(f"   - domain: {enriched_data.get('domain', '')}")

        return enriched_data

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析エラー: {e}")
        print(f"Response: {response[:200]}...")
        return None
    except Exception as e:
        print(f"❌ LLM処理エラー: {e}")
        return None


def save_to_db(comp_id: str, enriched_data: Dict[str, Any]) -> bool:
    """DBに保存"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # end_dateを使ってstatusを自動判定（LLMの判定より優先）
        if enriched_data.get('end_date'):
            try:
                end_date_obj = datetime.strptime(enriched_data['end_date'], "%Y-%m-%d").date()
                today = date.today()

                # 終了日が今日より前なら completed、今日以降なら active
                if end_date_obj < today:
                    enriched_data['status'] = 'completed'
                else:
                    enriched_data['status'] = 'active'
            except Exception:
                pass  # 日付パースエラーの場合はLLMの判定をそのまま使う

        # days_until_deadline を計算
        days_until_deadline = None
        if enriched_data.get('status') == 'active' and enriched_data.get('end_date'):
            try:
                end_date_obj = datetime.strptime(enriched_data['end_date'], "%Y-%m-%d").date()
                days_until = (end_date_obj - date.today()).days
                if days_until >= 0:
                    days_until_deadline = days_until
            except Exception:
                pass

        cursor.execute("""
            UPDATE competitions SET
                start_date = ?,
                end_date = ?,
                status = ?,
                metric = ?,
                metric_description = ?,
                summary = ?,
                tags = ?,
                data_types = ?,
                domain = ?,
                dataset_info = ?,
                days_until_deadline = ?,
                last_scraped_at = ?,
                competition_features = ?,
                task_types = ?
            WHERE id = ?
        """, (
            enriched_data.get('start_date'),
            enriched_data.get('end_date'),
            enriched_data.get('status'),
            enriched_data.get('metric'),
            enriched_data.get('metric_description'),
            enriched_data.get('summary'),
            json.dumps(enriched_data.get('tags', []), ensure_ascii=False),
            json.dumps(enriched_data.get('data_types', []), ensure_ascii=False),
            enriched_data.get('domain'),
            enriched_data.get('dataset_info'),
            days_until_deadline,
            datetime.now().isoformat(),
            json.dumps(enriched_data.get('competition_features', []), ensure_ascii=False),
            json.dumps(enriched_data.get('task_types', []), ensure_ascii=False),
            comp_id
        ))

        conn.commit()
        conn.close()

        print("[3/3] ✅ DB保存完了")
        return True

    except Exception as e:
        print(f"❌ DB保存エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main(limit=None, offset=0):
    """
    Args:
        limit: 処理する件数（Noneの場合は全件）
        offset: 開始位置（デフォルト0）
    """
    print("=" * 60)
    if limit:
        print(f"コンペ詳細情報の取得・整理（{offset}件目から{limit}件）")
    else:
        print(f"コンペ詳細情報の取得・整理（全件、{offset}件目から）")
    print("=" * 60)

    # サービス初期化
    scraper = get_scraper_service(cache_ttl_days=7)
    llm_service = get_llm_service()

    # コンペIDを取得
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    if limit:
        cursor.execute(f"SELECT id FROM competitions ORDER BY id LIMIT {limit} OFFSET {offset}")
    else:
        # 全件取得（offset指定時はLIMIT -1を使用）
        cursor.execute(f"SELECT id FROM competitions ORDER BY id LIMIT -1 OFFSET {offset}")
    comp_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"\n対象: {len(comp_ids)}件のコンペ")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for i, comp_id in enumerate(comp_ids, 1):
        print(f"\n進捗: {i}/{len(comp_ids)}")

        # 詳細取得＆構造化
        enriched_data = enrich_competition(comp_id, scraper, llm_service)

        if enriched_data:
            # DB保存
            if save_to_db(comp_id, enriched_data):
                success_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1

    # サマリー
    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)
    print(f"成功: {success_count}件")
    print(f"失敗: {failed_count}件")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='コンペティション詳細情報の取得・整理')
    parser.add_argument('--limit', type=int, default=None, help='処理する件数（デフォルト: 全件）')
    parser.add_argument('--offset', type=int, default=0, help='開始位置（デフォルト: 0）')
    parser.add_argument('--test', action='store_true', help='テストモード（1件のみ）')

    args = parser.parse_args()

    if args.test:
        limit = 1
        offset = 0
    else:
        limit = args.limit
        offset = args.offset

    try:
        main(limit=limit, offset=offset)
    except KeyboardInterrupt:
        print("\n\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
