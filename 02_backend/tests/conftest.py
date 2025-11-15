"""
pytest フィクスチャ定義

全テストで共通利用するフィクスチャを定義
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI テストクライアント"""
    from app.main import app

    return TestClient(app)
