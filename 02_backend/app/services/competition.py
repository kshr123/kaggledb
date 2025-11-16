"""
CompetitionService - コンペティションビジネスロジック
"""
from typing import Optional, List, Dict, Any

from app.repositories.competition import CompetitionRepository
from app.models.competition import Competition


class CompetitionService:
    """コンペティションサービス"""

    def __init__(self, repository: CompetitionRepository):
        """
        Args:
            repository: CompetitionRepository
        """
        self.repository = repository

    def get_competition(self, comp_id: str) -> Optional[Competition]:
        """
        コンペを取得

        Args:
            comp_id: コンペティションID

        Returns:
            Optional[Competition]: コンペティション（存在しない場合はNone）
        """
        return self.repository.get_by_id(comp_id)

    def list_competitions(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None,
    ) -> List[Competition]:
        """
        コンペ一覧を取得

        Args:
            limit: 取得件数
            offset: オフセット
            filters: フィルター条件
            sort_by: ソート項目
            order: ソート順（asc/desc）
            search: タイトル検索クエリ

        Returns:
            List[Competition]: コンペティション一覧
        """
        # 検索クエリがある場合は検索結果を返す
        if search:
            # 全件取得してフィルタリング（パフォーマンス改善の余地あり）
            all_comps = self.repository.list(
                limit=10000,
                offset=0,
                filters=filters,
                sort_by=sort_by,
                order=order
            )
            results = [
                comp for comp in all_comps
                if search.lower() in comp.title.lower()
            ]
            # ページネーション適用
            return results[offset:offset + limit]

        return self.repository.list(
            limit=limit,
            offset=offset,
            filters=filters,
            sort_by=sort_by,
            order=order
        )

    def create_competition(self, competition: Competition) -> Competition:
        """
        コンペを作成

        Args:
            competition: コンペティションモデル

        Returns:
            Competition: 作成されたコンペティション
        """
        return self.repository.create(competition)

    def update_competition(self, competition: Competition) -> Competition:
        """
        コンペを更新

        Args:
            competition: コンペティションモデル

        Returns:
            Competition: 更新されたコンペティション
        """
        return self.repository.update(competition)

    def delete_competition(self, comp_id: str) -> bool:
        """
        コンペを削除

        Args:
            comp_id: コンペティションID

        Returns:
            bool: 削除成功したかどうか
        """
        return self.repository.delete(comp_id)

    def count_competitions(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        コンペ数をカウント

        Args:
            filters: フィルター条件

        Returns:
            int: コンペ数
        """
        return self.repository.count(filters=filters)

    def search_competitions(self, query: str) -> List[Competition]:
        """
        コンペを検索（タイトル部分一致）

        Args:
            query: 検索クエリ

        Returns:
            List[Competition]: 検索結果
        """
        # すべてのコンペを取得して、タイトルで絞り込み
        all_comps = self.repository.list(limit=1000, offset=0)

        # タイトルに検索クエリが含まれるものをフィルタ
        results = [
            comp for comp in all_comps
            if query.lower() in comp.title.lower()
        ]

        return results

    def toggle_favorite(self, comp_id: str) -> Competition:
        """
        お気に入りトグル

        Args:
            comp_id: コンペティションID

        Returns:
            Competition: 更新されたコンペティション

        Raises:
            ValueError: コンペが存在しない場合
        """
        comp = self.repository.get_by_id(comp_id)
        if comp is None:
            raise ValueError(f"Competition {comp_id} not found")

        # is_favoriteを反転
        comp.is_favorite = not comp.is_favorite

        return self.repository.update(comp)
