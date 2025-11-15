"""
コンペティションAPI ルーター

GET /api/competitions - コンペ一覧取得
GET /api/competitions/{id} - コンペ詳細取得
GET /api/competitions/new - 新規コンペ取得
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException
import sqlite3
from app.config import DATABASE_PATH
from datetime import datetime, timedelta
import math

router = APIRouter()


@router.get("/competitions")
def get_competitions(
    page: int = Query(1, ge=1, description="ページ番号"),
    limit: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: Optional[str] = Query(None, description="ステータスフィルタ（active/completed）"),
    search: Optional[str] = Query(None, description="タイトル検索"),
    sort_by: str = Query("created_at", description="ソート項目"),
    order: str = Query("desc", description="ソート順（asc/desc）")
):
    """
    コンペ一覧を取得（ページネーション、フィルタ、検索、ソート対応）

    Args:
        page: ページ番号（1始まり）
        limit: 1ページあたりの件数（最大100）
        status: ステータスフィルタ（active/completed）
        search: タイトル検索（部分一致）
        sort_by: ソート項目（created_at, end_date など）
        order: ソート順（asc/desc）

    Returns:
        dict: {items: [...], total: int, page: int, limit: int, total_pages: int}
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # WHERE句の構築
    where_clauses = []
    params = []

    if status:
        where_clauses.append("status = ?")
        params.append(status)

    if search:
        where_clauses.append("title LIKE ?")
        params.append(f"%{search}%")

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # 総件数取得
    count_query = f"SELECT COUNT(*) as count FROM competitions WHERE {where_sql}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()["count"]

    # ソート順の検証と設定
    order_sql = "ASC" if order.lower() == "asc" else "DESC"

    # データ取得（ページネーション）
    offset = (page - 1) * limit
    data_query = f"""
        SELECT * FROM competitions
        WHERE {where_sql}
        ORDER BY {sort_by} {order_sql}
        LIMIT ? OFFSET ?
    """
    cursor.execute(data_query, params + [limit, offset])
    rows = cursor.fetchall()
    conn.close()

    # JSON形式に変換
    items = []
    for row in rows:
        item = dict(row)
        # JSON文字列をPythonリストに変換
        import json
        if item.get("tags"):
            item["tags"] = json.loads(item["tags"])
        if item.get("data_types"):
            item["data_types"] = json.loads(item["data_types"])
        items.append(item)

    # ページネーション情報
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/competitions/new")
def get_new_competitions(
    days: int = Query(30, ge=1, description="過去N日以内に追加されたコンペを取得"),
    limit: Optional[int] = Query(None, ge=1, description="取得件数の上限")
):
    """
    新規コンペを取得（created_at基準）

    Args:
        days: 過去N日以内（デフォルト30日）
        limit: 取得件数の上限

    Returns:
        list: 新規コンペ一覧
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # N日前の日付を計算
    cutoff_date = (datetime.now().date() - timedelta(days=days)).isoformat()

    # SQL構築
    query = """
        SELECT * FROM competitions
        WHERE created_at >= ?
        ORDER BY created_at DESC
    """

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, (cutoff_date,))
    rows = cursor.fetchall()
    conn.close()

    # JSON形式に変換
    items = []
    for row in rows:
        item = dict(row)
        import json
        if item.get("tags"):
            item["tags"] = json.loads(item["tags"])
        if item.get("data_types"):
            item["data_types"] = json.loads(item["data_types"])
        items.append(item)

    return items


@router.get("/competitions/{competition_id}")
def get_competition_by_id(competition_id: str):
    """
    コンペ詳細を取得

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: コンペ詳細情報

    Raises:
        HTTPException: コンペが見つからない場合は404
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM competitions WHERE id = ?", (competition_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Competition not found")

    # JSON形式に変換
    item = dict(row)
    import json
    if item.get("tags"):
        item["tags"] = json.loads(item["tags"])
    if item.get("data_types"):
        item["data_types"] = json.loads(item["data_types"])

    return item
