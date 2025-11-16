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


@router.get("/competitions/{competition_id}/discussions")
def get_competition_discussions(
    competition_id: str,
    sort_by: str = Query("vote_count", description="ソート項目（vote_count, comment_count, created_at）"),
    order: str = Query("desc", description="ソート順（asc/desc）"),
    limit: Optional[int] = Query(None, ge=1, description="取得件数の上限")
):
    """
    コンペティションのディスカッション一覧を取得

    Args:
        competition_id: コンペID（slug）
        sort_by: ソート項目（vote_count, comment_count, created_at）
        order: ソート順（asc/desc）
        limit: 取得件数の上限

    Returns:
        list: ディスカッション一覧
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ソート順の検証と設定
    order_sql = "ASC" if order.lower() == "asc" else "DESC"

    # ピン留めを優先してソート
    query = f"""
        SELECT * FROM discussions
        WHERE competition_id = ?
        ORDER BY is_pinned DESC, {sort_by} {order_sql}
    """

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, (competition_id,))
    rows = cursor.fetchall()
    conn.close()

    # JSON形式に変換
    discussions = [dict(row) for row in rows]

    return discussions


@router.get("/competitions/{competition_id}/solutions")
def get_competition_solutions(
    competition_id: str,
    sort_by: str = Query("rank", description="ソート項目（rank, vote_count, created_at）"),
    order: str = Query("asc", description="ソート順（asc/desc）"),
    limit: Optional[int] = Query(None, ge=1, description="取得件数の上限")
):
    """
    コンペティションの解法一覧を取得

    Args:
        competition_id: コンペID（slug）
        sort_by: ソート項目（rank, vote_count, created_at）
        order: ソート順（asc/desc）- rankの場合はascがデフォルト
        limit: 取得件数の上限

    Returns:
        list: 解法一覧
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ソート順の検証と設定
    order_sql = "ASC" if order.lower() == "asc" else "DESC"

    # rankがNULLのものは最後に表示
    if sort_by == "rank":
        query = f"""
            SELECT * FROM solutions
            WHERE competition_id = ?
            ORDER BY
                CASE WHEN rank IS NULL THEN 1 ELSE 0 END,
                rank {order_sql},
                vote_count DESC
        """
    else:
        query = f"""
            SELECT * FROM solutions
            WHERE competition_id = ?
            ORDER BY {sort_by} {order_sql}
        """

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, (competition_id,))
    rows = cursor.fetchall()
    conn.close()

    # JSON形式に変換
    solutions = [dict(row) for row in rows]

    return solutions


@router.patch("/competitions/{competition_id}/favorite")
def toggle_favorite(competition_id: str):
    """
    コンペティションのお気に入り状態を切り替える

    お気に入りをOFFにする場合、そのコンペのディスカッションも削除される

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 更新後のis_favorite状態と削除されたディスカッション数
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 現在の状態を取得
    cursor.execute("SELECT is_favorite FROM competitions WHERE id = ?", (competition_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Competition not found")

    # 現在の状態を反転
    current_state = row["is_favorite"]
    new_state = 0 if current_state else 1

    deleted_discussions = 0

    # お気に入りをOFFにする場合、ディスカッションも削除
    if new_state == 0:
        # 削除数を取得
        cursor.execute(
            "SELECT COUNT(*) as count FROM discussions WHERE competition_id = ?",
            (competition_id,)
        )
        deleted_discussions = cursor.fetchone()["count"]

        # ディスカッションを削除
        cursor.execute(
            "DELETE FROM discussions WHERE competition_id = ?",
            (competition_id,)
        )

    # お気に入り状態を更新
    cursor.execute(
        "UPDATE competitions SET is_favorite = ? WHERE id = ?",
        (new_state, competition_id)
    )
    conn.commit()
    conn.close()

    return {
        "is_favorite": bool(new_state),
        "deleted_discussions": deleted_discussions
    }


@router.post("/competitions/{competition_id}/discussions/fetch")
def fetch_discussions(competition_id: str):
    """
    コンペティションのディスカッションを取得してDBに保存

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 取得結果（新規保存数、更新数、合計数）
    """
    from app.services.scraper_service import get_scraper_service

    # コンペの存在確認
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM competitions WHERE id = ?", (competition_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Competition not found")

    conn.close()

    # スクレイピング実行
    scraper = get_scraper_service()
    discussions = scraper.get_discussions(
        comp_id=competition_id,
        max_pages=1,
        force_refresh=True  # 常に最新を取得
    )

    if not discussions:
        raise HTTPException(status_code=500, detail="Failed to fetch discussions")

    # データベースに保存
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    saved_count = 0
    updated_count = 0

    for disc in discussions:
        # 既存のレコードをチェック
        cursor.execute(
            "SELECT id FROM discussions WHERE competition_id = ? AND url = ?",
            (competition_id, disc['url'])
        )
        existing = cursor.fetchone()

        now = datetime.now().isoformat()

        if existing:
            # 更新
            cursor.execute("""
                UPDATE discussions
                SET title = ?,
                    author = ?,
                    author_tier = ?,
                    tier_color = ?,
                    vote_count = ?,
                    comment_count = ?,
                    category = ?,
                    is_pinned = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                disc['title'],
                disc['author'],
                disc.get('author_tier'),
                disc.get('tier_color'),
                disc['vote_count'],
                disc['comment_count'],
                disc['category'],
                disc['is_pinned'],
                now,
                existing[0]
            ))
            updated_count += 1
        else:
            # 新規作成
            cursor.execute("""
                INSERT INTO discussions (
                    competition_id,
                    title,
                    author,
                    author_tier,
                    tier_color,
                    url,
                    vote_count,
                    comment_count,
                    category,
                    is_pinned,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                competition_id,
                disc['title'],
                disc['author'],
                disc.get('author_tier'),
                disc.get('tier_color'),
                disc['url'],
                disc['vote_count'],
                disc['comment_count'],
                disc['category'],
                disc['is_pinned'],
                now,
                now
            ))
            saved_count += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "saved": saved_count,
        "updated": updated_count,
        "total": saved_count + updated_count
    }
