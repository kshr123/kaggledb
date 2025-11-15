#!/usr/bin/env python3
"""
評価指標更新スクリプト

既存のコンペティション情報の評価指標を更新します。
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime

from app.config import DATABASE_PATH
from app.services.kaggle_client import get_kaggle_client


def get_all_competition_ids():
    """データベースから全コンペティションIDを取得"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM competitions")
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids


def update_competition_metric(competition_id: str, metric: str) -> bool:
    """コンペティションの評価指標を更新"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE competitions SET metric = ?, updated_at = ? WHERE id = ?",
            (metric, datetime.now().isoformat(), competition_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 更新エラー ({competition_id}): {e}")
        return False


def main():
    print("=" * 60)
    print("評価指標更新スクリプト")
    print("=" * 60)

    # Kaggle APIクライアント初期化
    try:
        client = get_kaggle_client()
        print("✅ Kaggle APIクライアント初期化成功")
    except Exception as e:
        print(f"❌ Kaggle APIクライアント初期化失敗: {e}")
        return

    # 全コンペティションID取得
    competition_ids = get_all_competition_ids()
    print(f"📊 対象コンペティション数: {len(competition_ids)}")
    print("-" * 60)

    # Kaggle APIからコンペ一覧を取得（評価指標を含む）
    print("🔍 Kaggle APIからコンペティション情報を取得中...")
    all_competitions = []

    # ページネーションで全コンペを取得（最大5ページ）
    for page in range(1, 6):
        comps = client.get_competitions(page=page, search="")
        if not comps:
            break
        all_competitions.extend(comps)
        print(f"  ページ {page}: {len(comps)}件取得")

    print(f"✅ 合計 {len(all_competitions)}件のコンペティション情報を取得")
    print("-" * 60)

    # 評価指標を辞書に格納
    metrics_dict = {comp['id']: comp['metric'] for comp in all_competitions}

    # 各コンペティションの評価指標を更新
    success_count = 0
    not_found_count = 0

    for comp_id in competition_ids:
        if comp_id in metrics_dict:
            metric = metrics_dict[comp_id]
            if update_competition_metric(comp_id, metric):
                print(f"✅ {comp_id}: {metric}")
                success_count += 1
            else:
                print(f"❌ {comp_id}: 更新失敗")
        else:
            print(f"⚠️  {comp_id}: APIレスポンスに含まれていません")
            not_found_count += 1

    # サマリー
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)
    print(f"✅ 更新成功: {success_count}件")
    if not_found_count > 0:
        print(f"⚠️  APIに見つからず: {not_found_count}件")


if __name__ == "__main__":
    main()
