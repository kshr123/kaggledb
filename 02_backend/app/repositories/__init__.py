"""
リポジトリ層

データアクセスの抽象化を提供します。
"""
from .base import BaseRepository
from .competition import CompetitionRepository

__all__ = ["BaseRepository", "CompetitionRepository"]
