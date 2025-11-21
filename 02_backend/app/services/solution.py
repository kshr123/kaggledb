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

        print(f"\n=== 解法処理開始: {competition_id} ===", flush=True)
        print(f"受信アイテム数: {len(discussions_data)}件", flush=True)

        # 解法をフィルター
        # - category='writeup' のアイテムは全て解法
        # - それ以外はタイトルキーワードでフィルタリング
        solutions_data = []
        writeup_category_count = 0
        keyword_match_count = 0

        for disc in discussions_data:
            category = disc.get('category', '')

            # カテゴリが 'writeup' の場合は無条件で解法として扱う
            if category == 'writeup':
                writeup_category_count += 1
                clean_disc = disc.copy()
                clean_disc['title'] = self._clean_title(disc['title'], disc.get('author'))
                # Writeupsからランク情報を抽出
                _, rank = self._is_solution_discussion(disc['title'])
                clean_disc['rank'] = rank
                clean_disc['type'] = 'writeup'
                solutions_data.append(clean_disc)
                print(f"✓ Writeup: {clean_disc['title'][:50]}...", flush=True)
            else:
                # Discussionsはタイトルキーワードでフィルタリング
                is_solution, rank = self._is_solution_discussion(disc['title'])
                if is_solution:
                    keyword_match_count += 1
                    clean_disc = disc.copy()
                    clean_disc['title'] = self._clean_title(disc['title'], disc.get('author'))
                    clean_disc['rank'] = rank
                    clean_disc['type'] = 'discussion'
                    solutions_data.append(clean_disc)
                    print(f"✓ Solution (keyword): {clean_disc['title'][:50]}...", flush=True)

        print(f"\n=== フィルタリング完了 ===", flush=True)
        print(f"  - Writeups（category='writeup'）: {writeup_category_count}件", flush=True)
        print(f"  - タイトルキーワードマッチ: {keyword_match_count}件", flush=True)
        print(f"  - 合計解法数: {len(solutions_data)}件", flush=True)

        if not solutions_data:
            print("⚠ 解法が見つかりませんでした", flush=True)
            return {
                "saved": 0,
                "updated": 0,
                "total": 0,
                "ai_analyzed": 0
            }

        # 解法を保存
        print(f"\n=== 解法をDBに保存: {len(solutions_data)}件 ===", flush=True)
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
            # type: 'writeup' → 'discussion' にマッピング（DB制約対応）
            solution_type = 'discussion' if sol_data['type'] == 'writeup' else sol_data['type']

            solution = Solution(
                id=0,
                competition_id=competition_id,
                title=sol_data['title'],
                author=sol_data.get('author', ''),
                author_tier=sol_data.get('author_tier'),
                tier_color=sol_data.get('tier_color'),
                url=sol_data['url'],
                type=solution_type,
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
                print(f"  ✓ 更新: {solution.title[:50]}... (rank={solution.rank})", flush=True)
            else:
                saved_count += 1
                print(f"  ✓ 新規: {solution.title[:50]}... (rank={solution.rank})", flush=True)

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

        print(f"\n=== 解法保存完了 ===", flush=True)
        print(f"  新規保存: {saved_count}件", flush=True)
        print(f"  更新: {updated_count}件", flush=True)
        print(f"  合計: {saved_count + updated_count}件", flush=True)
        if enable_ai:
            print(f"  AI分析: {ai_analyzed_count}件", flush=True)

        return {
            "saved": saved_count,
            "updated": updated_count,
            "total": saved_count + updated_count,
            "ai_analyzed": ai_analyzed_count
        }

    def fetch_and_save_notebooks(
        self,
        competition_id: str,
        notebooks_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        ノートブック一覧をDBに保存（upsert）

        Args:
            competition_id: コンペティションID
            notebooks_data: スクレイピングで取得したノートブックデータのリスト

        Returns:
            dict: 保存結果（saved, updated, total）
        """
        saved_count = 0
        updated_count = 0

        print(f"\n=== ノートブック処理開始: {competition_id} ===", flush=True)
        print(f"受信アイテム数: {len(notebooks_data)}件", flush=True)

        if not notebooks_data:
            print("⚠ ノートブックが見つかりませんでした", flush=True)
            return {
                "saved": 0,
                "updated": 0,
                "total": 0
            }

        # ノートブックを保存
        print(f"\n=== ノートブックをDBに保存: {len(notebooks_data)}件 ===", flush=True)
        for nb_data in notebooks_data:
            # Solutionモデルを作成（type='notebook'）
            solution = Solution(
                id=0,
                competition_id=competition_id,
                title=nb_data['title'],
                author=nb_data.get('author', ''),
                author_tier=nb_data.get('author_tier'),
                tier_color=nb_data.get('tier_color'),
                url=nb_data['url'],
                type='notebook',  # ノートブックとして保存
                medal=None,  # ノートブックにはメダルなし
                rank=None,  # ノートブックにはランクなし
                vote_count=nb_data.get('vote_count', 0),
                comment_count=nb_data.get('comment_count', 0)
            )

            # 既存チェック
            existing = self._check_existing(competition_id, nb_data['url'])

            # upsert
            saved_solution = self.repository.upsert_by_url(solution)

            if existing:
                updated_count += 1
                print(f"  ✓ 更新: {solution.title[:50]}... (votes={solution.vote_count})", flush=True)
            else:
                saved_count += 1
                print(f"  ✓ 新規: {solution.title[:50]}... (votes={solution.vote_count})", flush=True)

        print(f"\n=== ノートブック保存完了 ===", flush=True)
        print(f"  新規保存: {saved_count}件", flush=True)
        print(f"  更新: {updated_count}件", flush=True)
        print(f"  合計: {saved_count + updated_count}件", flush=True)

        return {
            "saved": saved_count,
            "updated": updated_count,
            "total": saved_count + updated_count
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
