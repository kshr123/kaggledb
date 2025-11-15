"""
タグAPI ルーター

GET /api/tags - タグ一覧取得
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, Query
import sqlite3
from app.config import DATABASE_PATH

router = APIRouter()


@router.get("/tags")
def get_tags(
    category: Optional[str] = Query(None, description="タグカテゴリでフィルタ"),
    group_by_category: bool = Query(False, description="カテゴリ別にグルーピング")
):
    """
    タグ一覧を取得

    Args:
        category: タグカテゴリでフィルタ（data_type, task_type, model_type, solution_method, competition_feature, domain）
        group_by_category: カテゴリ別にグルーピングして返すか

    Returns:
        list: タグ一覧（デフォルト）
        dict: カテゴリ別タグ辞書（group_by_category=true の場合）
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 辞書形式で取得
    cursor = conn.cursor()

    # SQL クエリ構築
    if category:
        cursor.execute(
            "SELECT * FROM tags WHERE category = ? ORDER BY display_order",
            (category,)
        )
    else:
        cursor.execute("SELECT * FROM tags ORDER BY category, display_order")

    rows = cursor.fetchall()
    conn.close()

    # 辞書形式に変換
    tags = [dict(row) for row in rows]

    # カテゴリ別グルーピング
    if group_by_category:
        grouped = {}
        for tag in tags:
            cat = tag["category"]
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(tag)
        return grouped

    return tags
