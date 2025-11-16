"""
CompetitionRepository - コンペティションデータアクセス
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.competition import Competition


class CompetitionRepository(BaseRepository):
    """コンペティションリポジトリ"""

    def create(self, competition: Competition) -> Competition:
        """
        コンペを作成

        Args:
            competition: コンペティションモデル

        Returns:
            Competition: 作成されたコンペティション
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # 現在時刻をタイムスタンプとして使用
            now = datetime.now()

            cursor.execute(
                """
                INSERT INTO competitions (
                    id, title, url, start_date, end_date, status,
                    metric, metric_description, description, summary,
                    tags, data_types, domain, dataset_info,
                    discussion_count, solution_status, is_favorite,
                    created_at, updated_at, last_scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    competition.id,
                    competition.title,
                    competition.url,
                    competition.start_date.isoformat() if competition.start_date else None,
                    competition.end_date.isoformat() if competition.end_date else None,
                    competition.status,
                    competition.metric,
                    competition.metric_description,
                    competition.description,
                    competition.summary,
                    json.dumps(competition.tags) if competition.tags else None,
                    json.dumps(competition.data_types) if competition.data_types else None,
                    competition.domain,
                    competition.dataset_info,
                    competition.discussion_count or 0,
                    competition.solution_status or '未着手',
                    1 if competition.is_favorite else 0,
                    now.isoformat(),
                    now.isoformat(),
                    competition.last_scraped_at.isoformat() if competition.last_scraped_at else None,
                ),
            )
            conn.commit()

        return competition

    def get_by_id(self, comp_id: str) -> Optional[Competition]:
        """
        IDでコンペを取得

        Args:
            comp_id: コンペティションID

        Returns:
            Optional[Competition]: コンペティション（存在しない場合はNone）
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM competitions WHERE id = ?
                """,
                (comp_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_competition(row)

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> List[Competition]:
        """
        コンペ一覧を取得

        Args:
            limit: 取得件数
            offset: オフセット
            filters: フィルター条件
            sort_by: ソート項目（created_at, end_date, title など）
            order: ソート順（asc/desc）

        Returns:
            List[Competition]: コンペティション一覧
        """
        filters = filters or {}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # フィルター条件を構築
            where_clauses = []
            params = []

            for key, value in filters.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # ソート順の検証と設定
            order_sql = "ASC" if order.lower() == "asc" else "DESC"

            # クエリ実行
            cursor.execute(
                f"""
                SELECT * FROM competitions
                {where_sql}
                ORDER BY {sort_by} {order_sql}
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset],
            )
            rows = cursor.fetchall()

            return [self._row_to_competition(row) for row in rows]

    def update(self, competition: Competition) -> Competition:
        """
        コンペを更新

        Args:
            competition: コンペティションモデル

        Returns:
            Competition: 更新されたコンペティション
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now()

            cursor.execute(
                """
                UPDATE competitions SET
                    title = ?,
                    url = ?,
                    start_date = ?,
                    end_date = ?,
                    status = ?,
                    metric = ?,
                    metric_description = ?,
                    description = ?,
                    summary = ?,
                    tags = ?,
                    data_types = ?,
                    domain = ?,
                    dataset_info = ?,
                    discussion_count = ?,
                    solution_status = ?,
                    is_favorite = ?,
                    updated_at = ?,
                    last_scraped_at = ?
                WHERE id = ?
                """,
                (
                    competition.title,
                    competition.url,
                    competition.start_date.isoformat() if competition.start_date else None,
                    competition.end_date.isoformat() if competition.end_date else None,
                    competition.status,
                    competition.metric,
                    competition.metric_description,
                    competition.description,
                    competition.summary,
                    json.dumps(competition.tags) if competition.tags else None,
                    json.dumps(competition.data_types) if competition.data_types else None,
                    competition.domain,
                    competition.dataset_info,
                    competition.discussion_count or 0,
                    competition.solution_status or '未着手',
                    1 if competition.is_favorite else 0,
                    now.isoformat(),
                    competition.last_scraped_at.isoformat() if competition.last_scraped_at else None,
                    competition.id,
                ),
            )
            conn.commit()

        return competition

    def delete(self, comp_id: str) -> bool:
        """
        コンペを削除

        Args:
            comp_id: コンペティションID

        Returns:
            bool: 削除成功したかどうか
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM competitions WHERE id = ?
                """,
                (comp_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_new_competitions(
        self,
        days: int = 30,
        limit: Optional[int] = None
    ) -> List[Competition]:
        """
        新規コンペを取得（created_at基準）

        Args:
            days: 過去N日以内
            limit: 取得件数の上限

        Returns:
            List[Competition]: 新規コンペ一覧
        """
        from datetime import datetime, timedelta

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # N日前の日付を計算
            cutoff_date = (datetime.now().date() - timedelta(days=days)).isoformat()

            # SQL構築
            query = """
                SELECT * FROM competitions
                WHERE created_at >= ?
                ORDER BY created_at DESC
            """

            params = [cutoff_date]

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_competition(row) for row in rows]

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        コンペ数をカウント

        Args:
            filters: フィルター条件

        Returns:
            int: コンペ数
        """
        filters = filters or {}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # フィルター条件を構築
            where_clauses = []
            params = []

            for key, value in filters.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            cursor.execute(
                f"""
                SELECT COUNT(*) FROM competitions
                {where_sql}
                """,
                params,
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def _row_to_competition(self, row) -> Competition:
        """
        DB行をCompetitionモデルに変換

        Args:
            row: sqlite3.Row

        Returns:
            Competition: コンペティションモデル
        """
        data = dict(row)

        # datetimeフィールドを変換
        datetime_fields = ['start_date', 'end_date', 'created_at', 'updated_at', 'last_scraped_at']
        for field_name in datetime_fields:
            if data.get(field_name):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except (ValueError, TypeError):
                    data[field_name] = None

        # JSON文字列をリストに変換
        list_fields = ['tags', 'data_types']
        for field_name in list_fields:
            if data.get(field_name):
                try:
                    data[field_name] = json.loads(data[field_name])
                except (ValueError, TypeError, json.JSONDecodeError):
                    data[field_name] = []
            else:
                data[field_name] = []

        # is_favoriteをboolに変換
        if 'is_favorite' in data:
            data['is_favorite'] = bool(data['is_favorite'])

        return Competition.from_dict(data)
