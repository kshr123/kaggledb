"""
Competitionモデル
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class Competition:
    """コンペティション情報"""

    # 必須フィールド
    id: str
    title: str
    url: str
    status: str  # 'active', 'completed', 'upcoming'

    # オプショナルフィールド
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metric: Optional[str] = None
    metric_description: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    data_types: List[str] = field(default_factory=list)
    competition_features: List[str] = field(default_factory=list)
    task_types: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    dataset_info: Optional[str] = None  # JSON文字列
    discussion_count: int = 0
    solution_status: str = "未着手"
    is_favorite: bool = False

    # メタデータ
    created_at: Optional[datetime] = None
    last_scraped_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Dictに変換"""
        data = asdict(self)

        # datetimeをISO形式の文字列に変換
        for key in ['start_date', 'end_date', 'created_at', 'last_scraped_at']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Competition':
        """Dictから作成"""
        # datetimeフィールドを変換
        datetime_fields = ['start_date', 'end_date', 'created_at', 'last_scraped_at']
        for field_name in datetime_fields:
            if data.get(field_name) and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except (ValueError, TypeError):
                    data[field_name] = None

        # リストフィールドのデフォルト値
        if 'tags' not in data:
            data['tags'] = []
        if 'data_types' not in data:
            data['data_types'] = []
        if 'competition_features' not in data:
            data['competition_features'] = []
        if 'task_types' not in data:
            data['task_types'] = []

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
