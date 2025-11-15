"""
タグAPI のテスト（TDD: Red）

GET /api/tags エンドポイントのテスト
"""

import pytest
from fastapi.testclient import TestClient


class TestTagsAPI:
    """タグAPI のテストクラス"""

    def test_get_all_tags(self, client):
        """全タグの取得"""
        response = client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()

        # レスポンス形式の確認
        assert isinstance(data, list)
        assert len(data) == 60  # 全60タグ

        # タグオブジェクトの構造確認
        tag = data[0]
        assert "id" in tag
        assert "name" in tag
        assert "category" in tag
        assert "display_order" in tag

    def test_get_tags_grouped_by_category(self, client):
        """カテゴリ別グルーピングでタグを取得"""
        response = client.get("/api/tags?group_by_category=true")

        assert response.status_code == 200
        data = response.json()

        # グルーピングされたオブジェクト形式
        assert isinstance(data, dict)

        # 6つのカテゴリが存在
        assert len(data) == 6
        assert "data_type" in data
        assert "task_type" in data
        assert "model_type" in data
        assert "solution_method" in data
        assert "competition_feature" in data
        assert "domain" in data

        # 各カテゴリのタグ数確認
        assert len(data["data_type"]) == 7
        assert len(data["task_type"]) == 8
        assert len(data["model_type"]) == 15
        assert len(data["solution_method"]) == 12
        assert len(data["competition_feature"]) == 9
        assert len(data["domain"]) == 9

    def test_get_tags_by_category(self, client):
        """特定カテゴリのタグのみ取得"""
        response = client.get("/api/tags?category=data_type")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 7  # data_type は7タグ

        # すべて data_type カテゴリ
        for tag in data:
            assert tag["category"] == "data_type"

    def test_get_tags_invalid_category(self, client):
        """存在しないカテゴリを指定した場合"""
        response = client.get("/api/tags?category=invalid_category")

        assert response.status_code == 200
        data = response.json()

        # 空のリストを返す
        assert isinstance(data, list)
        assert len(data) == 0

    def test_tags_are_sorted_by_display_order(self, client):
        """タグが display_order でソートされているか"""
        response = client.get("/api/tags?category=data_type")

        assert response.status_code == 200
        data = response.json()

        # display_order が昇順になっているか確認
        display_orders = [tag["display_order"] for tag in data]
        assert display_orders == sorted(display_orders)
