"""
Solutionモデル
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Solution:
    """解法情報"""

    # 必須フィールド
    id: int
    competition_id: str
    title: str
    url: str
    author: str
    vote_count: int
    comment_count: int

    # オプショナルフィールド
    author_tier: Optional[str] = None
    tier_color: Optional[str] = None
    type: str = "discussion"  # 'discussion' or 'notebook'
    medal: Optional[str] = None  # 'gold', 'silver', 'bronze'
    rank: Optional[int] = None
    content: Optional[str] = None
    summary: Optional[str] = None  # JSON文字列
    techniques: Optional[str] = None  # JSON文字列

    # メタデータ
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Dictに変換"""
        data = asdict(self)

        # datetimeをISO形式の文字列に変換
        for key in ['created_at', 'updated_at']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Solution':
        """Dictから作成"""
        # datetimeフィールドを変換
        datetime_fields = ['created_at', 'updated_at']
        for field_name in datetime_fields:
            if data.get(field_name) and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except (ValueError, TypeError):
                    data[field_name] = None

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
