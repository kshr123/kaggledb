"""
SolutionRepository - 解法データアクセス
"""
from typing import Optional, List
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.solution import Solution


class SolutionRepository(BaseRepository):
    """解法リポジトリ"""

    def create(self, solution: Solution) -> Solution:
        """
        解法を作成

        Args:
            solution: Solutionモデル

        Returns:
            Solution: 作成された解法
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now()

            cursor.execute(
                """
                INSERT INTO solutions (
                    competition_id, title, author, author_tier, tier_color,
                    url, type, medal, rank, vote_count, comment_count,
                    content, summary, techniques, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    solution.competition_id,
                    solution.title,
                    solution.author,
                    solution.author_tier,
                    solution.tier_color,
                    solution.url,
                    solution.type,
                    solution.medal,
                    solution.rank,
                    solution.vote_count,
                    solution.comment_count,
                    solution.content,
                    solution.summary,
                    solution.techniques,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            conn.commit()

            # 作成されたIDを取得
            solution.id = cursor.lastrowid
            solution.created_at = now
            solution.updated_at = now

        return solution

    def get_by_id(self, solution_id: int) -> Optional[Solution]:
        """
        IDで解法を取得

        Args:
            solution_id: 解法ID

        Returns:
            Optional[Solution]: 解法（存在しない場合はNone）
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM solutions WHERE id = ?
                """,
                (solution_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_solution(row)

    def list_by_competition(
        self,
        competition_id: str,
        sort_by: str = "rank",
        order: str = "asc",
        limit: Optional[int] = None,
    ) -> List[Solution]:
        """
        コンペティションIDで解法一覧を取得

        Args:
            competition_id: コンペティションID
            sort_by: ソート項目（rank, vote_count, created_at）
            order: ソート順（asc/desc）
            limit: 取得件数の上限

        Returns:
            List[Solution]: 解法一覧
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # ソート順の検証と設定
            order_sql = "ASC" if order.lower() == "asc" else "DESC"

            # rankソートの場合、NULLは最後に表示
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

            return [self._row_to_solution(row) for row in rows]

    def update(self, solution: Solution) -> Solution:
        """
        解法を更新

        Args:
            solution: Solutionモデル

        Returns:
            Solution: 更新された解法
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now()

            cursor.execute(
                """
                UPDATE solutions SET
                    title = ?,
                    author = ?,
                    author_tier = ?,
                    tier_color = ?,
                    type = ?,
                    medal = ?,
                    rank = ?,
                    vote_count = ?,
                    comment_count = ?,
                    content = ?,
                    summary = ?,
                    techniques = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    solution.title,
                    solution.author,
                    solution.author_tier,
                    solution.tier_color,
                    solution.type,
                    solution.medal,
                    solution.rank,
                    solution.vote_count,
                    solution.comment_count,
                    solution.content,
                    solution.summary,
                    solution.techniques,
                    now.isoformat(),
                    solution.id,
                ),
            )
            conn.commit()

            solution.updated_at = now

        return solution

    def delete(self, solution_id: int) -> bool:
        """
        解法を削除

        Args:
            solution_id: 解法ID

        Returns:
            bool: 削除成功したかどうか
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM solutions WHERE id = ?
                """,
                (solution_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def upsert_by_url(self, solution: Solution) -> Solution:
        """
        URLで既存チェックしてinsert/updateを行う

        Args:
            solution: Solutionモデル

        Returns:
            Solution: 作成または更新された解法
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # URLで既存チェック
            cursor.execute(
                "SELECT id FROM solutions WHERE competition_id = ? AND url = ?",
                (solution.competition_id, solution.url)
            )
            existing = cursor.fetchone()

            if existing:
                # 更新
                solution.id = existing[0]
                return self.update(solution)
            else:
                # 新規作成
                return self.create(solution)

    def _row_to_solution(self, row) -> Solution:
        """
        DB行をSolutionモデルに変換

        Args:
            row: sqlite3.Row

        Returns:
            Solution: 解法モデル
        """
        data = dict(row)

        # datetimeフィールドを変換
        datetime_fields = ['created_at', 'updated_at']
        for field_name in datetime_fields:
            if data.get(field_name):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except (ValueError, TypeError):
                    data[field_name] = None

        return Solution.from_dict(data)
