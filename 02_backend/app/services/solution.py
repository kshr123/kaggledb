"""
SolutionService - 解法ビジネスロジック
"""
import re
from typing import List, Optional, Dict, Any, Tuple

from app.repositories.solution import SolutionRepository
from app.models.solution import Solution


class SolutionService:
    """解法サービス"""

    def __init__(self, repository: SolutionRepository):
        """
        Args:
            repository: SolutionRepository
        """
        self.repository = repository

    def get_solutions(
        self,
        competition_id: str,
        sort_by: str = "rank",
        order: str = "asc",
        limit: Optional[int] = None
    ) -> List[Solution]:
        """
        コンペティションの解法一覧を取得

        Args:
            competition_id: コンペティションID
            sort_by: ソート項目（rank, vote_count, created_at）
            order: ソート順（asc/desc）
            limit: 取得件数の上限

        Returns:
            List[Solution]: 解法一覧
        """
        return self.repository.list_by_competition(
            competition_id=competition_id,
            sort_by=sort_by,
            order=order,
            limit=limit
        )

    def fetch_and_save_solutions(
        self,
        competition_id: str,
        discussions_data: List[Dict[str, Any]],
        enable_ai: bool = False,
        scraper_service=None,
        llm_service=None
    ) -> Dict[str, int]:
        """
        ディスカッションから解法を抽出してDBに保存（upsert）

        Args:
            competition_id: コンペティションID
            discussions_data: スクレイピングで取得したディスカッションデータのリスト
            enable_ai: AI分析を有効にするか
            scraper_service: ScraperService インスタンス（AI分析時に必要）
            llm_service: LLMService インスタンス（AI分析時に必要）

        Returns:
            dict: 保存結果（saved, updated, total, ai_analyzed）
        """
        saved_count = 0
        updated_count = 0
        ai_analyzed_count = 0

        # 解法をフィルター
        solutions_data = []
        for disc in discussions_data:
            is_solution, rank = self._is_solution_discussion(disc['title'])
            if is_solution:
                clean_disc = disc.copy()
                clean_disc['title'] = self._clean_title(disc['title'], disc.get('author'))
                clean_disc['rank'] = rank
                clean_disc['type'] = 'discussion'
                solutions_data.append(clean_disc)

        if not solutions_data:
            return {
                "saved": 0,
                "updated": 0,
                "total": 0,
                "ai_analyzed": 0
            }

        # 解法を保存
        for sol_data in solutions_data:
            # メダル判定
            medal = None
            if sol_data.get('rank'):
                if sol_data['rank'] == 1:
                    medal = 'gold'
                elif sol_data['rank'] == 2:
                    medal = 'silver'
                elif sol_data['rank'] == 3:
                    medal = 'bronze'

            # Solutionモデルを作成
            solution = Solution(
                id=0,
                competition_id=competition_id,
                title=sol_data['title'],
                author=sol_data.get('author', ''),
                author_tier=sol_data.get('author_tier'),
                tier_color=sol_data.get('tier_color'),
                url=sol_data['url'],
                type=sol_data['type'],
                medal=medal,
                rank=sol_data.get('rank'),
                vote_count=sol_data['vote_count'],
                comment_count=sol_data['comment_count']
            )

            # 既存チェック
            existing = self._check_existing(competition_id, sol_data['url'])

            # upsert
            saved_solution = self.repository.upsert_by_url(solution)

            if existing:
                updated_count += 1
            else:
                saved_count += 1

            # AI分析
            if enable_ai and scraper_service and llm_service:
                # すでにsummaryとtechniquesがある場合はスキップ
                if saved_solution.summary and saved_solution.techniques:
                    continue

                # 解法の詳細を取得
                detail = scraper_service.get_discussion_detail(sol_data['url'])

                if detail and detail.get('content'):
                    content = detail['content']

                    # 要約生成
                    summary = llm_service.summarize_discussion(content, sol_data['title'])

                    # 技術抽出
                    techniques_json = llm_service.extract_solution_techniques(content, sol_data['title'])

                    # データベース更新（contentは保存しない）
                    saved_solution.summary = summary
                    saved_solution.techniques = techniques_json
                    self.repository.update(saved_solution)

                    ai_analyzed_count += 1

        return {
            "saved": saved_count,
            "updated": updated_count,
            "total": saved_count + updated_count,
            "ai_analyzed": ai_analyzed_count
        }

    def _clean_title(self, title: str, author: Optional[str] = None) -> str:
        """
        タイトルから余分な情報（投稿者、日付等）を除去

        Args:
            title: 元のタイトル
            author: 投稿者名

        Returns:
            str: クリーンなタイトル
        """
        if ' · ' in title:
            title = title.split(' · ')[0]
        if 'Last comment' in title:
            title = title.split('Last comment')[0]
        if 'Posted' in title:
            title = title.split('Posted')[0]
        if author and title.endswith(author):
            title = title[:-len(author)]
        return title.strip()

    def _is_solution_discussion(self, title: str) -> Tuple[bool, Optional[int]]:
        """
        タイトルから解法ディスカッションかどうかを判定

        Args:
            title: ディスカッションタイトル

        Returns:
            tuple: (is_solution, rank)
        """
        title_lower = title.lower()

        # 解法キーワード
        solution_keywords = [
            'solution', 'approach', 'write-up', 'writeup', '解法',
            'our solution', 'my solution'
        ]

        # ランクパターン
        rank_patterns = [
            r'(\d+)(?:st|nd|rd|th)\s+place',
            r'#(\d+)\s+solution',
            r'rank\s+(\d+)',
        ]

        has_solution_keyword = any(keyword in title_lower for keyword in solution_keywords)

        rank = None
        for pattern in rank_patterns:
            match = re.search(pattern, title_lower)
            if match:
                rank = int(match.group(1))
                break

        if rank:
            return True, rank
        if has_solution_keyword:
            return True, None
        return False, None

    def _check_existing(self, competition_id: str, url: str) -> bool:
        """
        URLで既存解法をチェック

        Args:
            competition_id: コンペティションID
            url: 解法URL

        Returns:
            bool: 既存の場合True
        """
        with self.repository.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM solutions WHERE competition_id = ? AND url = ?",
                (competition_id, url)
            )
            return cursor.fetchone() is not None
