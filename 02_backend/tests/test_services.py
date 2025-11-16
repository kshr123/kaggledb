"""
サービス層のテスト
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from app.database import Database
from app.repositories.competition import CompetitionRepository
from app.services.competition import CompetitionService
from app.models.competition import Competition


@pytest.fixture
def test_db():
    """テスト用データベース"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path)

    # テーブル作成
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE competitions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                status TEXT NOT NULL,
                metric TEXT,
                metric_description TEXT,
                description TEXT,
                summary TEXT,
                tags TEXT,
                data_types TEXT,
                domain TEXT,
                dataset_info TEXT,
                discussion_count INTEGER DEFAULT 0,
                solution_status TEXT DEFAULT '未着手',
                is_favorite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scraped_at TIMESTAMP
            )
        """)
        conn.commit()

    yield db

    # クリーンアップ
    Path(db_path).unlink(missing_ok=True)


class TestCompetitionService:
    """CompetitionServiceのテスト"""

    def test_create_service(self, test_db):
        """CompetitionServiceインスタンスを作成"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)
        assert service is not None

    def test_get_competition(self, test_db):
        """コンペを取得"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # データ作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )
        repo.create(comp)

        # サービス経由で取得
        result = service.get_competition("test-comp")

        assert result is not None
        assert result.id == "test-comp"
        assert result.title == "Test Competition"

    def test_get_competition_not_found(self, test_db):
        """存在しないコンペを取得するとNoneを返す"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        result = service.get_competition("non-existent")
        assert result is None

    def test_list_competitions(self, test_db):
        """コンペ一覧を取得"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # 複数作成
        for i in range(3):
            repo.create(Competition(
                id=f"comp-{i}",
                title=f"Competition {i}",
                url=f"https://kaggle.com/c/comp-{i}",
                status="active"
            ))

        # サービス経由で一覧取得
        results = service.list_competitions(limit=10, offset=0)

        assert len(results) == 3

    def test_list_competitions_with_filters(self, test_db):
        """フィルター付きでコンペ一覧を取得"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # 異なるステータスのコンペを作成
        repo.create(Competition(
            id="comp-1",
            title="Active Comp",
            url="https://kaggle.com/c/comp-1",
            status="active"
        ))
        repo.create(Competition(
            id="comp-2",
            title="Completed Comp",
            url="https://kaggle.com/c/comp-2",
            status="completed"
        ))

        # フィルター適用
        results = service.list_competitions(
            limit=10,
            offset=0,
            filters={"status": "active"}
        )

        assert len(results) == 1
        assert results[0].status == "active"

    def test_create_competition(self, test_db):
        """コンペを作成"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        comp = Competition(
            id="new-comp",
            title="New Competition",
            url="https://kaggle.com/c/new-comp",
            status="active"
        )

        result = service.create_competition(comp)

        assert result.id == "new-comp"
        assert result.title == "New Competition"

        # DBに保存されているか確認
        saved = repo.get_by_id("new-comp")
        assert saved is not None

    def test_update_competition(self, test_db):
        """コンペを更新"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # 作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )
        repo.create(comp)

        # 更新
        comp.title = "Updated Title"
        comp.summary = "Updated summary"
        result = service.update_competition(comp)

        assert result.title == "Updated Title"
        assert result.summary == "Updated summary"

    def test_delete_competition(self, test_db):
        """コンペを削除"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # 作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )
        repo.create(comp)

        # 削除
        result = service.delete_competition("test-comp")
        assert result is True

        # 確認
        deleted = repo.get_by_id("test-comp")
        assert deleted is None

    def test_count_competitions(self, test_db):
        """コンペ数をカウント"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # 3個作成
        for i in range(3):
            repo.create(Competition(
                id=f"comp-{i}",
                title=f"Competition {i}",
                url=f"https://kaggle.com/c/comp-{i}",
                status="active"
            ))

        count = service.count_competitions()
        assert count == 3

    def test_search_competitions(self, test_db):
        """コンペを検索（タイトル部分一致）"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # データ作成
        repo.create(Competition(
            id="nlp-comp",
            title="NLP Classification Challenge",
            url="https://kaggle.com/c/nlp-comp",
            status="active"
        ))
        repo.create(Competition(
            id="cv-comp",
            title="Computer Vision Challenge",
            url="https://kaggle.com/c/cv-comp",
            status="active"
        ))

        # 検索（タイトルに"NLP"を含む）
        results = service.search_competitions("NLP")

        assert len(results) == 1
        assert results[0].id == "nlp-comp"

    def test_toggle_favorite(self, test_db):
        """お気に入りトグル"""
        repo = CompetitionRepository(test_db)
        service = CompetitionService(repo)

        # コンペ作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active",
            is_favorite=False
        )
        repo.create(comp)

        # お気に入りON
        result = service.toggle_favorite("test-comp")
        assert result.is_favorite is True

        # お気に入りOFF
        result = service.toggle_favorite("test-comp")
        assert result.is_favorite is False
