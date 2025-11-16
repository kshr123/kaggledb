#!/usr/bin/env python3
"""
終了済みランクコンペ取得スクリプト

Kaggle APIから終了済みのランク有りコンペを取得してDBに保存
"""
import sys
import os

# プロジェクトルートからの相対パス
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, '02_backend')
sys.path.insert(0, backend_path)

from kaggle.api.kaggle_api_extended import KaggleApi
import sqlite3
from datetime import datetime
from app.config import DATABASE_PATH

def fetch_and_save_completed_competitions():
    """終了済みランクコンペを取得してDBに保存"""

    api = KaggleApi()
    api.authenticate()

    print("=" * 70)
    print("Kaggle APIから終了済みコンペを取得中...")
    print("=" * 70)

    # 複数ページ取得（最大200件）
    all_competitions = []
    for page in range(1, 11):  # 10ページ取得
        try:
            competitions = api.competitions_list(page=page, search='')
            if not competitions:
                break
            all_competitions.extend(competitions)
            print(f"Page {page}: {len(competitions)} competitions")
        except Exception as e:
            print(f"Page {page} fetch error: {e}")
            break

    print(f"\nTotal fetched: {len(all_competitions)} competitions\n")

    # ランクコンペをフィルター（進行中も含む）
    ranked_comps = []
    completed_ranked = []
    now = datetime.now()

    for comp in all_competitions:
        # ランクコンペの条件:
        # 1. reward に "Kudos" が含まれない（Kudosのみは非ランク）
        # 2. category が "Getting Started" でない

        is_ranked = (
            comp.reward and
            'Kudos' not in str(comp.reward) and
            comp.category != 'Getting Started'
        )

        if is_ranked:
            ranked_comps.append(comp)
            is_completed = comp.deadline and comp.deadline < now
            if is_completed:
                completed_ranked.append(comp)

    print(f"Ranked competitions: {len(ranked_comps)}")
    print(f"Completed ranked competitions: {len(completed_ranked)}\n")

    if not ranked_comps:
        print("❌ ランクコンペが見つかりませんでした")
        # デバッグ: 最初の3件を表示
        print("\nDebug - First 3 competitions:")
        for comp in all_competitions[:3]:
            print(f"  {comp.ref}: {comp.category}, reward={comp.reward}")
        return

    # 終了済みがなければ進行中のものも使用
    target_comps = completed_ranked if completed_ranked else ranked_comps
    print(f"Using {'completed' if completed_ranked else 'active'} competitions for DB: {len(target_comps)}\n")

    # DBに保存
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    saved_count = 0
    updated_count = 0

    for comp in target_comps[:20]:  # 最新20件のみ
        comp_id = comp.ref
        title = comp.title
        url = f"https://www.kaggle.com/competitions/{comp_id}"
        start_date = comp.enabled_date.date() if hasattr(comp, 'enabled_date') and comp.enabled_date else None
        end_date = comp.deadline.date() if comp.deadline else None
        status = 'complete' if (comp.deadline and comp.deadline < now) else 'active'
        description = comp.description or ''

        # 既存チェック
        cursor.execute("SELECT id FROM competitions WHERE id = ?", (comp_id,))
        existing = cursor.fetchone()

        now_str = datetime.now().isoformat()

        if existing:
            # 更新
            cursor.execute("""
                UPDATE competitions
                SET title = ?,
                    url = ?,
                    start_date = ?,
                    end_date = ?,
                    status = ?,
                    description = ?,
                    updated_at = ?
                WHERE id = ?
            """, (title, url, start_date, end_date, status, description, now_str, comp_id))
            updated_count += 1
        else:
            # 新規作成
            cursor.execute("""
                INSERT INTO competitions (
                    id, title, url, start_date, end_date, status, description,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (comp_id, title, url, start_date, end_date, status, description, now_str, now_str))
            saved_count += 1

        print(f"{'✓ 保存' if not existing else '✓ 更新'}: {comp_id} - {title[:50]}...")

    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print(f"✅ 完了: 新規{saved_count}件、更新{updated_count}件")
    print("=" * 70)

if __name__ == "__main__":
    fetch_and_save_completed_competitions()
