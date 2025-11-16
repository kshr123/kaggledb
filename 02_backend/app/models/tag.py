"""
Tagモデル
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Tag:
    """タグ情報"""

    # 必須フィールド
    name: str
    category: str  # 'technique', 'domain', 'data_type'
    display_order: int

    def to_dict(self) -> Dict[str, Any]:
        """Dictに変換"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tag':
        """Dictから作成"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
