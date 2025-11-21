"""
コンペティションAPI ルーター

GET /api/competitions - コンペ一覧取得
GET /api/competitions/{id} - コンペ詳細取得
GET /api/competitions/new - 新規コンペ取得
"""

from typing import Optional, Annotated, List
from fastapi import APIRouter, Query, HTTPException, Depends
import sqlite3
from app.config import DATABASE_PATH
from datetime import datetime, timedelta
import math

from app.database import get_database, Database
from app.repositories.competition import CompetitionRepository
from app.services.competition import CompetitionService

router = APIRouter()

from pydantic import BaseModel

class FavoriteUpdate(BaseModel):
    is_favorite: bool


# 依存性注入
def get_competition_service(db: Annotated[Database, Depends(get_database)]) -> CompetitionService:
    """CompetitionServiceのインスタンスを取得（依存性注入用）"""
    repository = CompetitionRepository(db)
    return CompetitionService(repository)


def get_discussion_service(db: Annotated[Database, Depends(get_database)]) -> "DiscussionService":
    """DiscussionServiceのインスタンスを取得（依存性注入用）"""
    from app.repositories.discussion import DiscussionRepository
    from app.services.discussion import DiscussionService
    repository = DiscussionRepository(db)
    return DiscussionService(repository)


def get_solution_service(db: Annotated[Database, Depends(get_database)]) -> "SolutionService":
    """SolutionServiceのインスタンスを取得（依存性注入用）"""
    from app.repositories.solution import SolutionRepository
    from app.services.solution import SolutionService
    repository = SolutionRepository(db)
    return SolutionService(repository)


@router.get("/competitions")
def get_competitions(
    page: int = Query(1, ge=1, description="ページ番号"),
    limit: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: Optional[str] = Query(None, description="ステータスフィルタ（active/completed）"),
    domain: Optional[str] = Query(None, description="ドメインフィルタ"),
    metrics: Optional[List[str]] = Query(None, description="評価指標フィルタ（複数可）"),
    data_types: Optional[List[str]] = Query(None, description="データタイプフィルタ（複数可）"),
    task_types: Optional[List[str]] = Query(None, description="タスク種別フィルタ（複数可）"),
    tags: Optional[List[str]] = Query(None, description="タグフィルタ（複数可）"),
    is_favorite: Optional[bool] = Query(None, description="お気に入りフィルタ"),
    search: Optional[str] = Query(None, description="タイトル検索"),
    sort_by: str = Query("created_at", description="ソート項目"),
    order: str = Query("desc", description="ソート順（asc/desc）"),
    service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペ一覧を取得（ページネーション、フィルタ、検索、ソート対応）

    Args:
        page: ページ番号（1始まり）
        limit: 1ページあたりの件数（最大100）
        status: ステータスフィルタ（active/completed）
        domain: ドメインフィルタ
        metrics: 評価指標フィルタ（複数選択可能）
        data_types: データタイプフィルタ（複数選択可能）
        tags: タグフィルタ（複数選択可能）
        search: タイトル検索（部分一致）
        sort_by: ソート項目（created_at, end_date など）
        order: ソート順（asc/desc）

    Returns:
        dict: {items: [...], total: int, page: int, limit: int, total_pages: int}
    """
    # フィルター構築
    filters = {}
    if status:
        filters["status"] = status
    if domain:
        filters["domain"] = domain
    if metrics:
        filters["metrics"] = metrics  # 複数のメトリックをリストで渡す
    if data_types:
        filters["data_types"] = data_types  # 複数のデータタイプをリストで渡す
    if task_types:
        filters["task_types"] = task_types  # 複数のタスク種別をリストで渡す
    if tags:
        filters["tags"] = tags  # 複数のタグをリストで渡す
    if is_favorite is not None:
        filters["is_favorite"] = is_favorite  # お気に入りフィルタ

    # ページネーション用のオフセット計算
    offset = (page - 1) * limit

    # サービス層を使用してデータ取得
    items = service.list_competitions(
        limit=limit,
        offset=offset,
        filters=filters,
        sort_by=sort_by,
        order=order,
        search=search
    )

    # 総件数取得（検索/フィルターを考慮）
    total = service.count_competitions(filters=filters)

    # 検索時の総件数調整（TODO: サービス層で最適化すべき）
    if search:
        # 検索結果の総件数を再計算
        all_items = service.list_competitions(
            limit=10000,
            offset=0,
            filters=filters,
            sort_by=sort_by,
            order=order,
            search=search
        )
        total = len(all_items)

    # ステータス別の統計情報を取得（全件対象）
    active_count = service.count_competitions(filters={"status": "active"})
    completed_count = service.count_competitions(filters={"status": "completed"})

    # ページネーション情報
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return {
        "items": [item.to_dict() for item in items],
        "total": total,
        "active_count": active_count,
        "completed_count": completed_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/competitions/new")
def get_new_competitions(
    days: int = Query(30, ge=1, description="過去N日以内に追加されたコンペを取得"),
    limit: Optional[int] = Query(None, ge=1, description="取得件数の上限"),
    service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    新規コンペを取得（created_at基準）

    Args:
        days: 過去N日以内（デフォルト30日）
        limit: 取得件数の上限

    Returns:
        list: 新規コンペ一覧
    """
    # サービス層を使用して新規コンペを取得
    competitions = service.get_new_competitions(days=days, limit=limit)

    return [comp.to_dict() for comp in competitions]


@router.get("/competitions/{competition_id}")
def get_competition_by_id(
    competition_id: str,
    service: Annotated[CompetitionService, Depends(get_competition_service)]
):
    """
    コンペ詳細を取得

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: コンペ詳細情報

    Raises:
        HTTPException: コンペが見つからない場合は404
    """
    competition = service.get_competition(competition_id)

    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    return competition.to_dict()


@router.get("/competitions/{competition_id}/discussions")
def get_competition_discussions(
    competition_id: str,
    sort_by: str = Query("vote_count", description="ソート項目（vote_count, comment_count, created_at）"),
    order: str = Query("desc", description="ソート順（asc/desc）"),
    limit: Optional[int] = Query(None, ge=1, description="取得件数の上限"),
    service: Annotated["DiscussionService", Depends(get_discussion_service)] = None
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
    discussions = service.get_discussions(
        competition_id=competition_id,
        sort_by=sort_by,
        order=order,
        limit=limit
    )

    return [disc.to_dict() for disc in discussions]


@router.get("/discussions/{discussion_id}")
def get_discussion(
    discussion_id: int,
    service: Annotated["DiscussionService", Depends(get_discussion_service)] = None
):
    """
    個別ディスカッションを取得

    Args:
        discussion_id: ディスカッションID

    Returns:
        dict: ディスカッション詳細
    """
    discussion = service.get_discussion(discussion_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    return discussion.to_dict()


@router.get("/discussions/{discussion_id}/content")
def get_discussion_content(discussion_id: int):
    """
    ディスカッションのコンテンツをRedisから取得

    Args:
        discussion_id: ディスカッションID

    Returns:
        dict: コンテンツ情報（原文と和訳）
    """
    from app.services.cache_service import get_cache_service

    cache = get_cache_service()

    # 原文コンテンツを取得
    content = cache.get_discussion_content(discussion_id)

    # 和訳コンテンツを取得
    translated_content = cache.get_discussion_content(f"{discussion_id}_translated")

    # TTL（残り有効期限）を取得
    ttl_seconds = cache.get_content_ttl(discussion_id=discussion_id)

    if not content and not translated_content:
        raise HTTPException(
            status_code=404,
            detail="Content not found in cache. Please fetch the discussion detail first."
        )

    return {
        "content": content,
        "translated_content": translated_content,
        "ttl_seconds": ttl_seconds,
        "ttl_days": round(ttl_seconds / 86400, 1) if ttl_seconds else None
    }


@router.post("/discussions/{discussion_id}/fetch")
def fetch_discussion_detail(
    discussion_id: int,
    service: Annotated["DiscussionService", Depends(get_discussion_service)] = None
):
    """
    ディスカッション詳細をスクレイピングして取得・保存

    コンテンツはRedisに3日間キャッシュ、要約のみDBに保存

    Args:
        discussion_id: ディスカッションID

    Returns:
        dict: 取得結果と更新されたディスカッション情報
    """
    from app.services.scraper_service import get_scraper_service
    from app.services.llm_service import get_llm_service
    from app.services.cache_service import get_cache_service

    # ディスカッションを取得
    discussion = service.get_discussion(discussion_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")

    # スクレイピング実行
    scraper = get_scraper_service()
    detail = scraper.get_discussion_detail(discussion.url)

    if not detail or not detail.get('content'):
        raise HTTPException(status_code=500, detail="Failed to fetch discussion detail")

    content = detail['content']

    # コンテンツをRedisに保存（3日間）
    cache = get_cache_service()
    cache.save_discussion_content(discussion_id, content)

    # リンク抽出
    links = extract_links_from_content(content)

    # LLMで構造化要約生成と和訳（学習用に詳細な要約を生成）
    llm = get_llm_service()
    structured_summary = None
    translated_content = None

    if len(content) > 200:  # 200文字以上の場合に処理
        # 構造化要約生成
        structured_summary = llm.generate_structured_discussion_summary(
            content=content,
            title=discussion.title
        )
        # 原文を和訳・整理
        translated_content = llm.translate_and_organize_discussion(content)

        # 和訳もRedisに保存（キーを分ける）
        if translated_content:
            cache.save_discussion_content(f"{discussion_id}_translated", translated_content)

    # データベース更新（contentはNULL、summaryのみ保存）
    discussion.content = None  # コンテンツはRedisに保存済み

    if structured_summary:
        discussion.summary = structured_summary

    updated_discussion = service.update_discussion(discussion)

    return {
        "success": True,
        "discussion": updated_discussion.to_dict(),
        "links": links,
        "content_cached_in_redis": True,
        "cache_ttl_days": 3
    }


@router.get("/competitions/{competition_id}/solutions")
def get_competition_solutions(
    competition_id: str,
    sort_by: str = Query("rank", description="ソート項目（rank, vote_count, created_at）"),
    order: str = Query("asc", description="ソート順（asc/desc）- rankの場合はascがデフォルト"),
    limit: Optional[int] = Query(None, ge=1, description="取得件数の上限"),
    service: Annotated["SolutionService", Depends(get_solution_service)] = None
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
    solutions = service.get_solutions(
        competition_id=competition_id,
        sort_by=sort_by,
        order=order,
        limit=limit
    )

    return [sol.to_dict() for sol in solutions]


@router.patch("/competitions/{competition_id}/favorite")
def toggle_favorite(
    competition_id: str,
    service: Annotated[CompetitionService, Depends(get_competition_service)]
):
    """
    コンペティションのお気に入り状態を切り替える

    お気に入りをOFFにする場合、そのコンペのディスカッションも削除される

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 更新後のis_favorite状態と削除されたディスカッション数
    """
    # 現在の状態を取得
    competition = service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    current_state = competition.is_favorite
    deleted_discussions = 0

    # お気に入りをOFFにする場合、ディスカッションも削除
    # TODO: この処理はDiscussionServiceに移動すべき
    if current_state:  # 現在ONなので、これからOFFになる
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 削除数を取得
        cursor.execute(
            "SELECT COUNT(*) as count FROM discussions WHERE competition_id = ?",
            (competition_id,)
        )
        result = cursor.fetchone()
        deleted_discussions = result[0] if result else 0

        # ディスカッションを削除
        cursor.execute(
            "DELETE FROM discussions WHERE competition_id = ?",
            (competition_id,)
        )
        conn.commit()
        conn.close()

    # お気に入り状態を更新（サービス層を使用）
    updated_competition = service.toggle_favorite(competition_id)

    return {
        "is_favorite": updated_competition.is_favorite,
        "deleted_discussions": deleted_discussions
    }


@router.post("/competitions/{competition_id}/discussions/fetch")
def fetch_discussions(
    competition_id: str,
    discussion_service: Annotated["DiscussionService", Depends(get_discussion_service)] = None,
    solution_service: Annotated["SolutionService", Depends(get_solution_service)] = None,
    competition_service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペティションのディスカッションとWriteupsを取得してDBに保存
    同時に解法も自動的に抽出・保存する

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 取得結果（ディスカッション・Writeups・解法の新規保存数、更新数、合計数）
    """
    print("\n" + "="*80, flush=True)
    print(f"[ENDPOINT] fetch_discussions called for {competition_id}", flush=True)
    print("="*80 + "\n", flush=True)

    from app.services.scraper_service import get_scraper_service

    # コンペの存在確認
    comp = competition_service.get_competition(competition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    # スクレイピング実行
    scraper = get_scraper_service()

    # Discussions + Writeups 両方を取得（新しい実装：重複除去済み）
    print("\n=== ディスカッション・Writeups取得開始（投票数順・3ページ）===", flush=True)
    all_items = scraper.get_discussions(
        comp_id=competition_id,
        max_pages=3,
        force_refresh=True
    )

    if not all_items:
        raise HTTPException(status_code=500, detail="Failed to fetch discussions and writeups")

    # カテゴリ別の集計
    writeup_items = [d for d in all_items if d.get('category') == 'writeup']
    discussion_items = [d for d in all_items if d.get('category') == 'discussion']

    writeup_count = len(writeup_items)
    discussion_count = len(discussion_items)

    print(f"✓ 取得完了: 合計 {len(all_items)}件（Discussions: {discussion_count}件、Writeups: {writeup_count}件）", flush=True)

    # Discussionsを保存（category='discussion' のみ）
    print(f"\n=== ディスカッション保存開始: {discussion_count}件 ===", flush=True)
    discussion_result = discussion_service.fetch_and_save_discussions(
        competition_id=competition_id,
        discussions_data=discussion_items
    )
    print(f"✓ ディスカッション保存完了: {discussion_result}", flush=True)

    # 4. 解法を抽出・保存（全データから）
    # - Writeups（category='writeup'）は全て解法
    # - Discussionsはタイトルキーワードでフィルタリング
    print(f"\n=== 解法抽出・保存開始: {len(all_items)}件のアイテムから ===", flush=True)
    solution_result = solution_service.fetch_and_save_solutions(
        competition_id=competition_id,
        discussions_data=all_items,
        enable_ai=False,
        scraper_service=None,
        llm_service=None
    )
    print(f"✓ 解法保存完了: {solution_result}", flush=True)

    return {
        "success": True,
        "discussions": discussion_result,
        "solutions": solution_result,
        "writeups_count": writeup_count,
        "total_items": len(all_items)
    }


@router.post("/competitions/{competition_id}/solutions/fetch")
def fetch_solutions(
    competition_id: str,
    enable_ai: bool = False,
    solution_service: Annotated["SolutionService", Depends(get_solution_service)] = None,
    competition_service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペティションの解法を取得してDBに保存

    Args:
        competition_id: コンペID（slug）
        enable_ai: AI分析を有効にするか（要約・技術抽出）

    Returns:
        dict: 取得結果（新規保存数、更新数、合計数、AI分析数）
    """
    from app.services.scraper_service import get_scraper_service
    from app.services.llm_service import get_llm_service

    # コンペの存在確認
    comp = competition_service.get_competition(competition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    # スクレイピング実行
    scraper = get_scraper_service()
    discussions = scraper.get_discussions(
        comp_id=competition_id,
        max_pages=3,  # 最大60件のディスカッションを取得
        force_refresh=True
    )

    if not discussions:
        raise HTTPException(status_code=500, detail="Failed to fetch discussions")

    # AI分析用のサービスを準備
    llm = get_llm_service() if enable_ai else None

    # サービス層で解法の抽出・保存・AI分析
    result = solution_service.fetch_and_save_solutions(
        competition_id=competition_id,
        discussions_data=discussions,
        enable_ai=enable_ai,
        scraper_service=scraper,
        llm_service=llm
    )

    return {
        "success": True,
        **result
    }


@router.post("/competitions/{competition_id}/notebooks/fetch")
def fetch_notebooks(
    competition_id: str,
    solution_service: Annotated["SolutionService", Depends(get_solution_service)] = None,
    competition_service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペティションのノートブック一覧を取得してDBに保存

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 取得結果（新規保存数、更新数、合計数）
    """
    from app.services.scraper_service import get_scraper_service

    # コンペの存在確認
    comp = competition_service.get_competition(competition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    # スクレイピング実行
    scraper = get_scraper_service()
    notebooks = scraper.get_notebooks(
        comp_id=competition_id,
        max_pages=3,  # 最大60件のノートブックを取得
        force_refresh=True
    )

    if not notebooks:
        return {
            "saved": 0,
            "updated": 0,
            "total": 0,
            "message": "ノートブックが見つかりませんでした"
        }

    # DBに保存
    result = solution_service.fetch_and_save_notebooks(
        competition_id=competition_id,
        notebooks_data=notebooks
    )

    return {
        **result,
        "message": f"{result['total']}件のノートブックを保存しました"
    }


@router.get("/competitions/{competition_id}/notebooks")
def get_notebooks(
    competition_id: str,
    sort_by: str = Query("vote_count", description="ソート項目（vote_count, created_at）"),
    order: str = Query("desc", description="ソート順（asc/desc）"),
    limit: Optional[int] = Query(None, description="取得件数の上限")
):
    """
    コンペティションのノートブック一覧を取得

    Args:
        competition_id: コンペID
        sort_by: ソート項目
        order: ソート順
        limit: 取得件数の上限

    Returns:
        List[Solution]: ノートブック一覧（type='notebook'のもののみ）
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ソート項目の検証
    allowed_sort_fields = ["vote_count", "created_at", "title"]
    if sort_by not in allowed_sort_fields:
        sort_by = "vote_count"

    # ソート順の検証
    if order.lower() not in ["asc", "desc"]:
        order = "desc"

    # クエリ構築
    query = f"""
        SELECT * FROM solutions
        WHERE competition_id = ? AND type = 'notebook'
        ORDER BY {sort_by} {order.upper()}
    """

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, (competition_id,))
    notebooks = cursor.fetchall()
    conn.close()

    return [dict(nb) for nb in notebooks]


def extract_links_from_content(content: str) -> dict:
    """
    本文からリンクを抽出

    Args:
        content: 本文

    Returns:
        dict: {
            "notebooks": [...],
            "github": [...],
            "other": [...]
        }
    """
    import re

    # URLパターン
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'

    # 全URLを抽出
    urls = re.findall(url_pattern, content)

    # カテゴリ分け
    notebooks = []
    github = []
    other = []

    for url in urls:
        # 重複排除
        if 'kaggle.com/code/' in url or 'kaggle.com/notebooks/' in url:
            if url not in notebooks:
                notebooks.append(url)
        elif 'github.com/' in url:
            if url not in github:
                github.append(url)
        else:
            if url not in other:
                other.append(url)

    return {
        "notebooks": notebooks[:5],  # 最大5件
        "github": github[:5],
        "other": other[:5]
    }


@router.get("/solutions/{solution_id}/content")
def get_solution_content(solution_id: int):
    """
    解法のコンテンツをRedisから取得

    Args:
        solution_id: 解法ID

    Returns:
        dict: コンテンツ情報（原文と和訳）
    """
    from app.services.cache_service import get_cache_service

    cache = get_cache_service()

    # 原文コンテンツを取得
    content = cache.get_solution_content(solution_id)

    # 和訳コンテンツを取得
    translated_content = cache.get_solution_content(f"{solution_id}_translated")

    # TTL（残り有効期限）を取得
    ttl_seconds = cache.get_content_ttl(solution_id=solution_id)

    if not content and not translated_content:
        raise HTTPException(
            status_code=404,
            detail="Content not found in cache. Please fetch the solution detail first."
        )

    return {
        "content": content,
        "translated_content": translated_content,
        "ttl_seconds": ttl_seconds,
        "ttl_days": round(ttl_seconds / 86400, 1) if ttl_seconds else None
    }


@router.post("/solutions/{solution_id}/fetch")
def fetch_solution_detail(solution_id: int):
    """
    解法詳細をスクレイピングして取得・保存

    コンテンツはRedisに3日間キャッシュ、要約と技術情報のみDBに保存

    Args:
        solution_id: 解法ID

    Returns:
        dict: 取得結果と更新された解法情報
    """
    from app.services.scraper_service import get_scraper_service
    from app.services.llm_service import get_llm_service
    from app.services.cache_service import get_cache_service

    # 解法の存在確認
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM solutions WHERE id = ?", (solution_id,))
    solution = cursor.fetchone()

    if not solution:
        conn.close()
        raise HTTPException(status_code=404, detail="Solution not found")

    solution_dict = dict(solution)
    conn.close()

    # スクレイピング実行
    scraper = get_scraper_service()
    detail = scraper.get_discussion_detail(solution_dict['url'])

    if not detail or not detail.get('content'):
        raise HTTPException(status_code=500, detail="Failed to fetch solution content")

    content = detail['content']

    # コンテンツをRedisに保存（3日間）
    cache = get_cache_service()
    cache.save_solution_content(solution_id, content)

    # リンク抽出
    links = extract_links_from_content(content)

    # LLMで構造化要約生成と和訳
    llm = get_llm_service()
    structured_summary = None
    translated_content = None

    if len(content) > 200:  # 200文字以上の場合に処理
        # 構造化要約生成
        structured_summary = llm.generate_structured_solution_summary(
            content=content,
            title=solution_dict['title']
        )
        # 原文を和訳・整理
        translated_content = llm.translate_and_organize_discussion(content)

        # 和訳もRedisに保存
        if translated_content:
            cache.save_solution_content(f"{solution_id}_translated", translated_content)

    # 技術抽出
    techniques_json = llm.extract_solution_techniques(content, solution_dict['title'])

    # データベース更新（contentはNULL、summaryとtechniquesのみ保存）
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE solutions
        SET content = NULL,
            summary = ?,
            techniques = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        structured_summary,
        techniques_json,
        datetime.now().isoformat(),
        solution_id
    ))

    conn.commit()

    # 更新後の解法を取得
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM solutions WHERE id = ?", (solution_id,))
    updated_solution = dict(cursor.fetchone())
    conn.close()

    return {
        "success": True,
        "solution": updated_solution,
        "links": links,
        "content_cached_in_redis": True,
        "cache_ttl_days": 3
    }


@router.post("/competitions/{competition_id}/data/fetch")
def fetch_dataset_info(
    competition_id: str,
    competition_service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペティションのデータタブ情報を取得してDBに保存

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 取得結果
    """
    # コンペティションが存在するか確認
    competition = competition_service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # スクレイパーとLLMサービスを取得
    from app.services.scraper_service import get_scraper_service
    from app.services.llm_service import get_llm_service

    scraper = get_scraper_service()
    llm = get_llm_service()

    # Data タブをスクレイピング
    data_tab_content = scraper.get_tab_content(competition_id, tab="data")

    if not data_tab_content or not data_tab_content.get('full_text'):
        raise HTTPException(status_code=500, detail="Failed to scrape data tab")

    # LLMでデータセット情報を抽出
    dataset_info = llm.extract_dataset_info(
        data_text=data_tab_content['full_text'],
        title=competition.title
    )

    if not dataset_info:
        raise HTTPException(status_code=500, detail="Failed to extract dataset info")

    # データセット情報を完全なJSON形式で保存
    import json
    dataset_info_json = json.dumps(dataset_info, ensure_ascii=False)

    # データベース更新
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE competitions
        SET dataset_info = ?
        WHERE id = ?
    """, (
        dataset_info_json,
        competition_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "dataset_info": dataset_info  # 構造化データを返す
    }


@router.post("/competitions/{competition_id}/summary/generate")
def generate_competition_summary(
    competition_id: str,
    competition_service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペティションの概要（description）からLLM要約を生成

    Args:
        competition_id: コンペID（slug）

    Returns:
        dict: 生成結果
    """
    # コンペティションが存在するか確認
    competition = competition_service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # すでに要約がある場合は返す
    if competition.summary:
        import json
        try:
            summary = json.loads(competition.summary)
            return {
                "success": True,
                "summary": summary,
                "cached": True
            }
        except json.JSONDecodeError:
            # JSON解析エラーの場合は再生成
            pass

    # descriptionがない場合はエラー
    if not competition.description:
        raise HTTPException(status_code=400, detail="Competition has no description")

    # LLMで要約を生成
    from app.services.llm_service import get_llm_service
    llm = get_llm_service()

    summary_json = llm.generate_summary(
        description=competition.description,
        title=competition.title,
        metric=competition.metric or ""
    )

    if not summary_json:
        raise HTTPException(status_code=500, detail="Failed to generate summary")

    # データベース更新
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE competitions
        SET summary = ?
        WHERE id = ?
    """, (summary_json, competition_id))

    conn.commit()
    conn.close()

    # 要約を返す
    import json
    summary = json.loads(summary_json)
    return {
        "success": True,
        "summary": summary,
        "cached": False
    }


@router.post("/notebooks/{notebook_id}/summarize")
def summarize_notebook(
    notebook_id: int,
    solution_service: Annotated["SolutionService", Depends(get_solution_service)] = None
):
    """
    ノートブックの要約を生成

    Args:
        notebook_id: ノートブックID（solutionsテーブルのid）

    Returns:
        要約のJSON
    """
    import json
    from app.services.scraper_service import get_scraper_service
    from app.services.llm_service import get_llm_service

    # 1. データベースからノートブック情報を取得
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM solutions
        WHERE id = ? AND type = 'notebook'
    """, (notebook_id,))

    notebook = cursor.fetchone()

    if not notebook:
        conn.close()
        raise HTTPException(status_code=404, detail="Notebook not found")

    notebook_dict = dict(notebook)

    # すでに要約がある場合は返す
    if notebook_dict.get('summary'):
        conn.close()
        try:
            summary = json.loads(notebook_dict['summary'])
            return {
                "success": True,
                "summary": summary,
                "cached": True
            }
        except json.JSONDecodeError:
            # JSON解析エラーの場合は再生成
            pass

    # 2. スクレイパーでノートブックのコンテンツを取得
    scraper = get_scraper_service()
    detail = scraper.get_discussion_detail(notebook_dict['url'])

    if not detail or not detail.get('content'):
        conn.close()
        raise HTTPException(status_code=500, detail="Failed to fetch notebook content")

    content = detail['content']

    # コンテンツをRedisに保存（3日間）
    from app.services.cache_service import get_cache_service
    cache = get_cache_service()
    cache.save_solution_content(notebook_id, content)

    # 3. LLMで要約を生成
    llm = get_llm_service()
    summary_json = llm.summarize_notebook(
        content=content,
        title=notebook_dict['title']
    )

    if not summary_json or summary_json == "{}":
        conn.close()
        raise HTTPException(status_code=500, detail="Failed to generate summary")

    # 4. データベースに保存（contentは保存しない）
    cursor.execute("""
        UPDATE solutions
        SET summary = ?
        WHERE id = ?
    """, (summary_json, notebook_id))

    conn.commit()
    conn.close()

    # 5. 要約を返す
    summary = json.loads(summary_json)
    return {
        "success": True,
        "summary": summary,
        "cached": False,
        "content_cached_in_redis": True,
        "cache_ttl_days": 3
    }
