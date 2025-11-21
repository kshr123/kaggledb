"""
Kaggle API Client

Kaggle APIを使ってコンペティション情報を取得するクライアント
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi


class KaggleClient:
    """Kaggle API クライアント"""

    def __init__(self):
        """初期化（環境変数から認証情報を読み込む）"""
        self.api = KaggleApi()
        self.api.authenticate()

    def get_competitions(
        self,
        page: int = 1,
        search: str = "",
        category: str = None
    ) -> List[Dict]:
        """
        コンペティション一覧を取得

        Args:
            page: ページ番号
            search: 検索キーワード
            category: カテゴリ（"featured", "research", "playground", "gettingStarted"）

        Returns:
            コンペティション情報のリスト
        """
        try:
            # Kaggle APIからコンペ一覧を取得
            params = {"page": page, "search": search}
            if category:
                params["category"] = category

            competitions = self.api.competitions_list(**params)

            result = []
            for comp in competitions:
                try:
                    result.append(self._format_competition(comp))
                except Exception as e:
                    print(f"Error formatting competition {comp.ref}: {e}")
                    continue

            return result

        except Exception as e:
            print(f"Error fetching competitions: {e}")
            return []

    def get_competition_detail(self, competition_id: str) -> Optional[Dict]:
        """
        コンペティション詳細を取得

        Args:
            competition_id: コンペティションID（slug）

        Returns:
            コンペティション詳細情報
        """
        try:
            # Kaggle APIで検索して取得（competition_viewメソッドは存在しないため）
            comps = self.api.competitions_list(search=competition_id)

            # 完全一致するものを探す
            for comp in comps:
                comp_id = comp.ref
                if isinstance(comp_id, str) and comp_id.startswith('http'):
                    comp_id = comp_id.rstrip('/').split('/')[-1]

                if comp_id == competition_id:
                    return self._format_competition(comp)

            # 見つからない場合
            return None

        except Exception as e:
            print(f"Error fetching competition {competition_id}: {e}")
            return None

    def _format_competition(self, comp) -> Dict:
        """
        Kaggle APIのレスポンスを整形

        Args:
            comp: Kaggle APIのCompetitionオブジェクト

        Returns:
            整形されたコンペティション情報
        """
        # ステータスの判定
        now = datetime.now()

        # 日付の処理
        try:
            if hasattr(comp, 'enabledDate') and comp.enabledDate:
                start_date = comp.enabledDate.isoformat() if hasattr(comp.enabledDate, 'isoformat') else str(comp.enabledDate)
            else:
                start_date = None

            if hasattr(comp, 'deadline') and comp.deadline:
                end_date = comp.deadline.isoformat() if hasattr(comp.deadline, 'isoformat') else str(comp.deadline)
                deadline = comp.deadline if hasattr(comp.deadline, 'year') else datetime.fromisoformat(comp.deadline)
                status = "active" if deadline > now else "completed"
            else:
                end_date = None
                status = "completed"  # デフォルトは終了済み

        except Exception as e:
            print(f"Error parsing dates for {comp.ref}: {e}")
            start_date = None
            end_date = None
            status = "completed"

        # 評価指標の取得
        metric = getattr(comp, 'evaluation_metric', 'Unknown')

        # 説明文の取得
        description = getattr(comp, 'description', '')

        # IDの取得（comp.refがURLの場合はslugを抽出）
        competition_id = comp.ref
        if isinstance(competition_id, str) and competition_id.startswith('http'):
            # URLからslugを抽出（例: https://www.kaggle.com/competitions/titanic → titanic）
            competition_id = competition_id.rstrip('/').split('/')[-1]

        # URLの構築
        url = f"https://www.kaggle.com/c/{competition_id}"

        return {
            "id": competition_id,  # kaggle競技のslug（例: titanic）
            "title": comp.title,
            "url": url,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "metric": metric,
            "description": description,
            "summary": "",  # LLMで生成するため空
            "tags": [],  # LLMで生成するため空
            "data_types": [],  # LLMで生成するため空
            "domain": "",  # LLMで生成するため空
            "discussion_count": 0,
            "solution_status": "未着手",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def test_connection(self) -> bool:
        """
        Kaggle API接続テスト

        Returns:
            接続成功の場合True
        """
        try:
            # 簡単なAPI呼び出しでテスト
            self.api.competitions_list(page=1)
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# シングルトンインスタンス
_kaggle_client = None


def get_kaggle_client() -> KaggleClient:
    """Kaggle APIクライアントのシングルトンインスタンスを取得"""
    global _kaggle_client
    if _kaggle_client is None:
        _kaggle_client = KaggleClient()
    return _kaggle_client
