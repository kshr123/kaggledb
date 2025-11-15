#!/usr/bin/env python3
"""
MABeコンペのタグを修正
"""

import sys
import os

# バックエンドディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_backend'))

import sqlite3
import json
from datetime import datetime

from app.config import DATABASE_PATH
from app.services.llm_service import get_llm_service

def get_available_tags():
    """タグマスタを取得"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, category FROM tags ORDER BY category, display_order")
    rows = cursor.fetchall()

    tags_by_category = {}
    for name, category in rows:
        if category not in tags_by_category:
            tags_by_category[category] = []
        tags_by_category[category].append(name)

    conn.close()
    return tags_by_category

def get_competition(comp_id: str):
    """コンペティション情報を取得"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, metric, tags, data_types, domain, summary
        FROM competitions
        WHERE id = ?
    """, (comp_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    comp = dict(row)
    comp['tags'] = json.loads(comp.get('tags', '[]') or '[]')
    comp['data_types'] = json.loads(comp.get('data_types', '[]') or '[]')

    return comp

def update_competition(comp):
    """コンペティション情報を更新"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE competitions
        SET tags = ?, data_types = ?, domain = ?, summary = ?, updated_at = ?
        WHERE id = ?
    """, (
        json.dumps(comp['tags'], ensure_ascii=False),
        json.dumps(comp['data_types'], ensure_ascii=False),
        comp['domain'],
        comp['summary'],
        datetime.now().isoformat(),
        comp['id']
    ))

    conn.commit()
    conn.close()

def main():
    print("=" * 60)
    print("MABe タグ修正")
    print("=" * 60)

    # LLMサービス初期化
    llm_service = get_llm_service()
    print("✅ LLMサービス初期化成功")

    # タグマスタ取得
    available_tags = get_available_tags()
    print(f"✅ タグマスタ取得: {sum(len(t) for t in available_tags.values())}件")

    # MABeコンペ取得
    comp = get_competition('MABe-mouse-behavior-detection')
    if not comp:
        print("❌ MABeコンペが見つかりません")
        return

    print(f"\n📊 {comp['title']}")
    print(f"説明: {comp['description']}")
    print(f"現在のタグ: {comp['tags']}")

    # タグ生成
    print("\nタグ再生成中...")
    tag_result = llm_service.generate_tags(
        description=comp['description'],
        title=comp['title'],
        metric=comp['metric'],
        available_tags=available_tags
    )

    # 要約生成
    print("要約再生成中...")
    summary = llm_service.generate_summary(
        description=comp['description'],
        title=comp['title']
    )

    # 更新
    comp['tags'] = tag_result.get('tags', [])
    comp['data_types'] = tag_result.get('data_types', [])
    comp['domain'] = tag_result.get('domain', '')
    comp['summary'] = summary

    print(f"\n✅ 新しいタグ: {comp['tags']}")
    print(f"✅ データタイプ: {comp['data_types']}")
    print(f"✅ ドメイン: {comp['domain']}")

    update_competition(comp)
    print("💾 データベース更新完了")

if __name__ == "__main__":
    main()
