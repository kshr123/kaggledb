"""
DiscussionRepository - ディスカッションデータアクセス
"""
from typing import Optional, List
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.discussion import Discussion


class DiscussionRepository(BaseRepository):
    """ディスカッションリポジトリ"""

    def create(self, discussion: Discussion) -> Discussion:
        """
        ディスカッションを作成

        Args:
            discussion: Discussionモデル

        Returns:
            Discussion: 作成されたディスカッション
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now()

            cursor.execute(
                """
                INSERT INTO discussions (
                    competition_id, title, author, author_tier, tier_color,
                    url, vote_count, comment_count, category, is_pinned,
                    content, summary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    discussion.competition_id,
                    discussion.title,
                    discussion.author,
                    discussion.author_tier,
                    discussion.tier_color,
                    discussion.url,
                    discussion.vote_count,
                    discussion.comment_count,
                    discussion.category,
                    1 if discussion.is_pinned else 0,
                    discussion.content,
                    discussion.summary,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
            conn.commit()

            # 作成されたIDを取得
            discussion.id = cursor.lastrowid
            discussion.created_at = now
            discussion.updated_at = now

        return discussion

    def get_by_id(self, discussion_id: int) -> Optional[Discussion]:
        """
        IDでディスカッションを取得

        Args:
            discussion_id: ディスカッションID

        Returns:
            Optional[Discussion]: ディスカッション（存在しない場合はNone）
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM discussions WHERE id = ?
                """,
                (discussion_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_discussion(row)

    def list_by_competition(
        self,
        competition_id: str,
        sort_by: str = "vote_count",
        order: str = "desc",
        limit: Optional[int] = None,
    ) -> List[Discussion]:
        """
        コンペティションIDでディスカッション一覧を取得

        Args:
            competition_id: コンペティションID
            sort_by: ソート項目（vote_count, comment_count, created_at）
            order: ソート順（asc/desc）
            limit: 取得件数の上限

        Returns:
            List[Discussion]: ディスカッション一覧
        """
        with self.db.get_connection() as conn:
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

            return [self._row_to_discussion(row) for row in rows]

    def update(self, discussion: Discussion) -> Discussion:
        """
        ディスカッションを更新

        Args:
            discussion: Discussionモデル

        Returns:
            Discussion: 更新されたディスカッション
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now()

            cursor.execute(
                """
                UPDATE discussions SET
                    title = ?,
                    author = ?,
                    author_tier = ?,
                    tier_color = ?,
                    vote_count = ?,
                    comment_count = ?,
                    category = ?,
                    is_pinned = ?,
                    content = ?,
                    summary = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    discussion.title,
                    discussion.author,
                    discussion.author_tier,
                    discussion.tier_color,
                    discussion.vote_count,
                    discussion.comment_count,
                    discussion.category,
                    1 if discussion.is_pinned else 0,
                    discussion.content,
                    discussion.summary,
                    now.isoformat(),
                    discussion.id,
                ),
            )
            conn.commit()

            discussion.updated_at = now

        return discussion

    def delete(self, discussion_id: int) -> bool:
        """
        ディスカッションを削除

        Args:
            discussion_id: ディスカッションID

        Returns:
            bool: 削除成功したかどうか
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM discussions WHERE id = ?
                """,
                (discussion_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def upsert_by_url(self, discussion: Discussion) -> Discussion:
        """
        URLで既存チェックしてinsert/updateを行う

        Args:
            discussion: Discussionモデル

        Returns:
            Discussion: 作成または更新されたディスカッション
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # URLで既存チェック
            cursor.execute(
                "SELECT id FROM discussions WHERE competition_id = ? AND url = ?",
                (discussion.competition_id, discussion.url)
            )
            existing = cursor.fetchone()

            if existing:
                # 更新
                discussion.id = existing[0]
                return self.update(discussion)
            else:
                # 新規作成
                return self.create(discussion)

    def _row_to_discussion(self, row) -> Discussion:
        """
        DB行をDiscussionモデルに変換

        Args:
            row: sqlite3.Row

        Returns:
            Discussion: ディスカッションモデル
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

        # is_pinnedをboolに変換
        if 'is_pinned' in data:
            data['is_pinned'] = bool(data['is_pinned'])

        return Discussion.from_dict(data)
