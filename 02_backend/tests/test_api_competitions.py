"""
コンペティションAPI のテスト（TDD: Red）

GET /api/competitions - コンペ一覧取得
GET /api/competitions/{id} - コンペ詳細取得
GET /api/competitions/new - 新規コンペ取得
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


@pytest.fixture
def sample_competitions(client):
    """テスト用のサンプルコンペティションを挿入"""
    import sqlite3
    from app.config import DATABASE_PATH

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 既存のコンペティションを削除
    cursor.execute("DELETE FROM competitions")

    # サンプルデータ挿入
    today = datetime.now().date()
    samples = [
        # 開催中のコンペ（2件）
        (
            "housing-prices-2025",
            "Housing Prices Prediction 2025",
            "https://www.kaggle.com/c/housing-prices-2025",
            (today - timedelta(days=30)).isoformat(),
            (today + timedelta(days=15)).isoformat(),
            "active",
            "RMSE",
            "Predict housing prices using 79 features",
            "住宅価格を予測するコンペ。79個の特徴量を使った回帰タスク。",
            '["テーブルデータ", "回帰"]',
            '["テーブルデータ"]',
            "金融",
            0,
            "未着手",
            today.isoformat(),
            today.isoformat()
        ),
        (
            "image-classification-2025",
            "Image Classification Challenge 2025",
            "https://www.kaggle.com/c/image-classification-2025",
            (today - timedelta(days=20)).isoformat(),
            (today + timedelta(days=25)).isoformat(),
            "active",
            "Accuracy",
            "Classify images into 10 categories",
            "10カテゴリの画像分類タスク。",
            '["画像", "分類（多クラス）"]',
            '["画像"]',
            "コンピュータビジョン",
            0,
            "未着手",
            today.isoformat(),
            today.isoformat()
        ),
        # 終了済みのコンペ（1件）
        (
            "titanic",
            "Titanic - Machine Learning from Disaster",
            "https://www.kaggle.com/c/titanic",
            "2012-09-28",
            "2020-12-31",
            "completed",
            "Accuracy",
            "Predict survival on the Titanic",
            "タイタニック号の生存者予測。",
            '["テーブルデータ", "分類（二値）"]',
            '["テーブルデータ"]',
            "その他",
            5,
            "ディスカッションのみ",
            (today - timedelta(days=60)).isoformat(),
            today.isoformat()
        ),
        # 新規コンペ（7日前に追加）
        (
            "nlp-sentiment-2025",
            "NLP Sentiment Analysis 2025",
            "https://www.kaggle.com/c/nlp-sentiment-2025",
            (today - timedelta(days=5)).isoformat(),
            (today + timedelta(days=60)).isoformat(),
            "active",
            "F1 Score",
            "Sentiment analysis on movie reviews",
            "映画レビューの感情分析。",
            '["テキスト", "分類（多クラス）"]',
            '["テキスト"]',
            "自然言語処理",
            0,
            "未着手",
            (today - timedelta(days=7)).isoformat(),
            today.isoformat()
        ),
    ]

    cursor.executemany("""
        INSERT INTO competitions (
            id, title, url, start_date, end_date, status, metric,
            description, summary, tags, data_types, domain,
            discussion_count, solution_status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, samples)

    conn.commit()
    conn.close()

    yield

    # クリーンアップ
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM competitions")
    conn.commit()
    conn.close()


class TestCompetitionsListAPI:
    """コンペ一覧API のテスト"""

    def test_get_all_competitions(self, client, sample_competitions):
        """全コンペの取得"""
        response = client.get("/api/competitions")

        assert response.status_code == 200
        data = response.json()

        # ページネーション形式
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data

        # 全4件取得
        assert data["total"] == 4
        assert len(data["items"]) == 4

    def test_get_competitions_with_pagination(self, client, sample_competitions):
        """ページネーション"""
        response = client.get("/api/competitions?page=1&limit=2")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 4
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["limit"] == 2
        assert data["total_pages"] == 2

    def test_get_competitions_filter_by_status(self, client, sample_competitions):
        """ステータスでフィルタ"""
        response = client.get("/api/competitions?status=active")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3  # active は3件
        for item in data["items"]:
            assert item["status"] == "active"

    def test_get_competitions_search(self, client, sample_competitions):
        """検索"""
        response = client.get("/api/competitions?search=housing")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 1
        # タイトルに "housing" を含む
        assert any("housing" in item["title"].lower() for item in data["items"])

    def test_get_competitions_sort_by_end_date(self, client, sample_competitions):
        """終了日でソート"""
        response = client.get("/api/competitions?sort_by=end_date&order=asc")

        assert response.status_code == 200
        data = response.json()

        # 終了日が昇順
        end_dates = [item["end_date"] for item in data["items"]]
        assert end_dates == sorted(end_dates)


class TestCompetitionDetailAPI:
    """コンペ詳細API のテスト"""

    def test_get_competition_by_id(self, client, sample_competitions):
        """IDでコンペ詳細を取得"""
        response = client.get("/api/competitions/housing-prices-2025")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == "housing-prices-2025"
        assert data["title"] == "Housing Prices Prediction 2025"
        assert data["status"] == "active"
        assert data["metric"] == "RMSE"
        assert "summary" in data
        assert "tags" in data
        assert "data_types" in data

    def test_get_competition_not_found(self, client, sample_competitions):
        """存在しないコンペ"""
        response = client.get("/api/competitions/nonexistent-comp")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestNewCompetitionsAPI:
    """新規コンペAPI のテスト"""

    def test_get_new_competitions_default(self, client, sample_competitions):
        """新規コンペ取得（デフォルト30日）"""
        response = client.get("/api/competitions/new")

        assert response.status_code == 200
        data = response.json()

        # 7日前に作成されたコンペが含まれる
        assert len(data) >= 1
        assert any(item["id"] == "nlp-sentiment-2025" for item in data)

    def test_get_new_competitions_custom_days(self, client, sample_competitions):
        """新規コンペ取得（カスタム日数）"""
        response = client.get("/api/competitions/new?days=5")

        assert response.status_code == 200
        data = response.json()

        # 7日前のコンペは含まれない（5日以内のみ）
        assert not any(item["id"] == "nlp-sentiment-2025" for item in data)

    def test_get_new_competitions_with_limit(self, client, sample_competitions):
        """新規コンペ取得（件数制限）"""
        response = client.get("/api/competitions/new?limit=1")

        assert response.status_code == 200
        data = response.json()

        assert len(data) <= 1
