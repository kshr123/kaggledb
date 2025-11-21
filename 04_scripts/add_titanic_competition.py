#!/usr/bin/env python3
"""
Titanicコンペティションをデータベースに追加するスクリプト
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
from datetime import datetime
from kaggle import api
from app.config import DATABASE_PATH


def add_titanic():
    """Titanicコンペティションをデータベースに追加"""

    print("=" * 60)
    print("Titanicコンペティションを追加")
    print("=" * 60)

    # Kaggle API認証
    print("\n[1/3] Kaggle API接続中...")
    api.authenticate()
    print("✅ 接続成功")

    # Titanicコンペティション情報を取得
    print("\n[2/3] Titanicコンペティション情報を取得中...")
    comps = api.competitions_list(search='titanic')

    # 正確なTitanicを取得
    titanic = None
    for c in comps:
        if 'titanic' in c.ref and 'spaceship' not in c.ref.lower():
            titanic = c
            break

    if not titanic:
        print("❌ Titanicコンペティションが見つかりませんでした")
        return

    # URLからslugを抽出（IDとして使用）
    comp_slug = titanic.ref.split('/')[-1]

    print(f"✅ 取得: {titanic.title}")
    print(f"   Slug: {comp_slug}")
    print(f"   URL: {titanic.url}")

    # データベースに保存
    print("\n[3/3] データベースに保存中...")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存チェック
    cursor.execute("SELECT id FROM competitions WHERE id = ?", (comp_slug,))
    existing = cursor.fetchone()

    now = datetime.now().isoformat()

    if existing:
        print(f"   既に存在します: {comp_slug}")
        # 更新
        cursor.execute("""
            UPDATE competitions SET
                title = ?,
                url = ?,
                start_date = ?,
                end_date = ?,
                status = ?,
                metric = ?,
                description = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            titanic.title,
            titanic.url,
            titanic.enabled_date.isoformat() if titanic.enabled_date else None,
            titanic.deadline.isoformat() if titanic.deadline else None,
            'completed' if titanic.deadline and titanic.deadline < datetime.now() else 'active',
            titanic.evaluation_metric if hasattr(titanic, 'evaluation_metric') else 'Unknown',
            titanic.description if hasattr(titanic, 'description') else '',
            now,
            comp_slug
        ))
        print("   📝 更新しました")
    else:
        # 新規挿入
        cursor.execute("""
            INSERT INTO competitions (
                id, title, url, start_date, end_date, status, metric,
                description, summary, tags, data_types, domain,
                discussion_count, solution_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            comp_slug,
            titanic.title,
            titanic.url,
            titanic.enabled_date.isoformat() if titanic.enabled_date else None,
            titanic.deadline.isoformat() if titanic.deadline else None,
            'completed' if titanic.deadline and titanic.deadline < datetime.now() else 'active',
            titanic.evaluation_metric if hasattr(titanic, 'evaluation_metric') else 'Unknown',
            titanic.description if hasattr(titanic, 'description') else '',
            '{}',  # summary（JSON文字列）
            '["Binary Classification", "Structured Data"]',  # tags
            '["Tabular"]',  # data_types
            'Education',  # domain
            0,  # discussion_count（後で更新）
            '未着手',  # solution_status
            now,
            now
        ))
        print("   ✅ 新規追加しました")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        add_titanic()
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
