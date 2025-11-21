"""
DiscussionService - ディスカッションビジネスロジック
"""
from typing import List, Optional, Dict, Any

from app.repositories.discussion import DiscussionRepository
from app.models.discussion import Discussion


class DiscussionService:
    """ディスカッションサービス"""

    def __init__(self, repository: DiscussionRepository):
        """
        Args:
            repository: DiscussionRepository
        """
        self.repository = repository

    def get_discussions(
        self,
        competition_id: str,
        sort_by: str = "vote_count",
        order: str = "desc",
        limit: Optional[int] = None
    ) -> List[Discussion]:
        """
        コンペティションのディスカッション一覧を取得

        Args:
            competition_id: コンペティションID
            sort_by: ソート項目（vote_count, comment_count, created_at）
            order: ソート順（asc/desc）
            limit: 取得件数の上限

        Returns:
            List[Discussion]: ディスカッション一覧
        """
        return self.repository.list_by_competition(
            competition_id=competition_id,
            sort_by=sort_by,
            order=order,
            limit=limit
        )

    def get_discussion(self, discussion_id: int) -> Optional[Discussion]:
        """
        個別ディスカッションを取得

        Args:
            discussion_id: ディスカッションID

        Returns:
            Optional[Discussion]: ディスカッション（存在しない場合はNone）
        """
        return self.repository.get_by_id(discussion_id)

    def update_discussion(self, discussion: Discussion) -> Discussion:
        """
        ディスカッションを更新

        Args:
            discussion: ディスカッションモデル

        Returns:
            Discussion: 更新されたディスカッション
        """
        return self.repository.update(discussion)

    def fetch_and_save_discussions(
        self,
        competition_id: str,
        discussions_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        ディスカッションデータをDBに保存（upsert）

        Args:
            competition_id: コンペティションID
            discussions_data: スクレイピングで取得したディスカッションデータのリスト

        Returns:
            dict: 保存結果（saved: 新規保存数, updated: 更新数, total: 合計）
        """
        saved_count = 0
        updated_count = 0

        for disc_data in discussions_data:
            # Discussionモデルを作成
            discussion = Discussion(
                id=0,  # upsert時に設定される
                competition_id=competition_id,
                title=disc_data['title'],
                author=disc_data['author'],
                author_tier=disc_data.get('author_tier'),
                tier_color=disc_data.get('tier_color'),
                url=disc_data['url'],
                vote_count=disc_data['vote_count'],
                comment_count=disc_data['comment_count'],
                category=disc_data.get('category'),
                is_pinned=disc_data.get('is_pinned', False)
            )

            # URLで既存チェックしてupsert
            # upsert_by_url内で新規/更新を判定
            # 既存の場合はupdated_count、新規の場合はsaved_count をインクリメント
            # この情報を返すためには、upsert_by_url の戻り値を拡張する必要がある
            # 簡易的に、保存前にチェック
            existing = self._check_existing(competition_id, disc_data['url'])

            self.repository.upsert_by_url(discussion)

            if existing:
                updated_count += 1
            else:
                saved_count += 1

        return {
            "saved": saved_count,
            "updated": updated_count,
            "total": saved_count + updated_count
        }

    def _check_existing(self, competition_id: str, url: str) -> bool:
        """
        URLで既存ディスカッションをチェック

        Args:
            competition_id: コンペティションID
            url: ディスカッションURL

        Returns:
            bool: 既存の場合True
        """
        # リポジトリのget_connection を使用して直接チェック
        with self.repository.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM discussions WHERE competition_id = ? AND url = ?",
                (competition_id, url)
            )
            return cursor.fetchone() is not None
