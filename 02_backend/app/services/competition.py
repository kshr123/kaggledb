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
            search: タイトルまたは評価指標での検索クエリ

        Returns:
            List[Competition]: コンペティション一覧
        """
        # data_types、task_types、tags フィルターを抽出（JSON配列なのでPython側でフィルタリング）
        data_types_filter = filters.pop('data_types', None) if filters else None
        task_types_filter = filters.pop('task_types', None) if filters else None
        tags_filter = filters.pop('tags', None) if filters else None

        # 検索クエリまたはJSON配列フィルターがある場合は全件取得してフィルタリング
        if search or data_types_filter or task_types_filter or tags_filter:
            # 全件取得してフィルタリング（パフォーマンス改善の余地あり）
            all_comps = self.repository.list(
                limit=10000,
                offset=0,
                filters=filters,
                sort_by=sort_by,
                order=order
            )

            results = all_comps

            # タイトルまたは評価指標で検索
            if search:
                results = [
                    comp for comp in results
                    if search.lower() in comp.title.lower() or
                       (comp.metric and search.lower() in comp.metric.lower())
                ]

            # data_typesでフィルタリング（OR検索：いずれかのデータタイプを含む）
            if data_types_filter:
                results = [
                    comp for comp in results
                    if comp.data_types and any(dt in comp.data_types for dt in data_types_filter)
                ]

            # task_typesでフィルタリング（OR検索：いずれかのタスク種別を含む）
            if task_types_filter:
                results = [
                    comp for comp in results
                    if comp.task_types and any(tt in comp.task_types for tt in task_types_filter)
                ]

            # tagsでフィルタリング（OR検索：いずれかのタグを含む）
            if tags_filter:
                results = [
                    comp for comp in results
                    if comp.tags and any(tag in comp.tags for tag in tags_filter)
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
        # data_types と tags フィルターがある場合はPython側でフィルタリング
        if filters and ('data_types' in filters or 'tags' in filters):
            # フィルターのコピーを作成
            filters_copy = filters.copy()
            data_types_filter = filters_copy.pop('data_types', None)
            tags_filter = filters_copy.pop('tags', None)

            # 全件取得してフィルタリング
            all_comps = self.repository.list(
                limit=10000,
                offset=0,
                filters=filters_copy,
                sort_by="created_at",
                order="desc"
            )

            results = all_comps

            # data_typesでフィルタリング（OR検索：いずれかのデータタイプを含む）
            if data_types_filter:
                results = [
                    comp for comp in results
                    if comp.data_types and any(dt in comp.data_types for dt in data_types_filter)
                ]

            # tagsでフィルタリング（OR検索：いずれかのタグを含む）
            if tags_filter:
                results = [
                    comp for comp in results
                    if comp.tags and any(tag in comp.tags for tag in tags_filter)
                ]

            return len(results)

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

    def get_new_competitions(
        self,
        days: int = 30,
        limit: Optional[int] = None
    ) -> List[Competition]:
        """
        新規コンペを取得（created_at基準）

        Args:
            days: 過去N日以内（デフォルト30日）
            limit: 取得件数の上限

        Returns:
            List[Competition]: 新規コンペ一覧
        """
        return self.repository.get_new_competitions(days=days, limit=limit)

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
