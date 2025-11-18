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
    competition_service: Annotated[CompetitionService, Depends(get_competition_service)] = None
):
    """
    コンペティションのディスカッションを取得してDBに保存

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
    discussions = scraper.get_discussions(
        comp_id=competition_id,
        max_pages=1,
        force_refresh=True  # 常に最新を取得
    )

    if not discussions:
        raise HTTPException(status_code=500, detail="Failed to fetch discussions")

    # サービス層で保存
    result = discussion_service.fetch_and_save_discussions(
        competition_id=competition_id,
        discussions_data=discussions
    )

    return {
        "success": True,
        **result
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


@router.post("/solutions/{solution_id}/summarize")
def summarize_solution(solution_id: int):
    """
    個別の解法を要約（オンデマンド）

    Args:
        solution_id: 解法ID

    Returns:
        dict: 構造化された要約とリンク
    """
    from app.services.scraper_service import get_scraper_service
    from app.services.llm_service import get_llm_service

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

    # 解法の詳細を取得
    scraper = get_scraper_service()
    detail = scraper.get_discussion_detail(solution_dict['url'])

    if not detail or not detail.get('content'):
        raise HTTPException(status_code=500, detail="Failed to fetch solution content")

    content = detail['content']

    # リンク抽出
    links = extract_links_from_content(content)

    # 構造化要約を生成
    llm = get_llm_service()
    structured_summary = llm.generate_structured_solution_summary(
        content=content,
        title=solution_dict['title']
    )

    # 技術抽出
    techniques_json = llm.extract_solution_techniques(content, solution_dict['title'])

    # データベース更新（contentは保存しない）
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE solutions
        SET summary = ?,
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
    conn.close()

    return {
        "success": True,
        "summary": structured_summary,
        "techniques": techniques_json,
        "links": links
    }
