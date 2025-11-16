"""
リポジトリ層のテスト
"""
import pytest
import sqlite3
from datetime import datetime
from pathlib import Path
import tempfile

from app.database import Database
from app.repositories.base import BaseRepository
from app.repositories.competition import CompetitionRepository
from app.models.competition import Competition


@pytest.fixture
def test_db():
    """テスト用データベース"""
    # 一時ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    # データベース初期化
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


class TestDatabase:
    """Database接続管理のテスト"""

    def test_create_database_instance(self, test_db):
        """Databaseインスタンスを作成"""
        assert test_db is not None
        assert isinstance(test_db, Database)

    def test_get_connection(self, test_db):
        """DB接続を取得"""
        with test_db.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)

    def test_connection_context_manager(self, test_db):
        """コンテキストマネージャーでDB接続を管理"""
        with test_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1


class TestBaseRepository:
    """BaseRepositoryのテスト"""

    def test_create_base_repository(self, test_db):
        """BaseRepositoryインスタンスを作成"""
        repo = BaseRepository(test_db)
        assert repo is not None
        assert repo.db == test_db


class TestCompetitionRepository:
    """CompetitionRepositoryのテスト"""

    def test_create_competition_repository(self, test_db):
        """CompetitionRepositoryインスタンスを作成"""
        repo = CompetitionRepository(test_db)
        assert repo is not None

    def test_create_competition(self, test_db):
        """コンペを作成"""
        repo = CompetitionRepository(test_db)
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )

        result = repo.create(comp)

        assert result.id == "test-comp"
        assert result.title == "Test Competition"

    def test_get_by_id(self, test_db):
        """IDでコンペを取得"""
        repo = CompetitionRepository(test_db)

        # まず作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )
        repo.create(comp)

        # 取得
        result = repo.get_by_id("test-comp")

        assert result is not None
        assert result.id == "test-comp"
        assert result.title == "Test Competition"

    def test_get_by_id_not_found(self, test_db):
        """存在しないIDで取得するとNoneを返す"""
        repo = CompetitionRepository(test_db)
        result = repo.get_by_id("non-existent")
        assert result is None

    def test_list_competitions(self, test_db):
        """コンペ一覧を取得"""
        repo = CompetitionRepository(test_db)

        # 複数作成
        for i in range(3):
            comp = Competition(
                id=f"comp-{i}",
                title=f"Competition {i}",
                url=f"https://kaggle.com/c/comp-{i}",
                status="active"
            )
            repo.create(comp)

        # 一覧取得
        results = repo.list(limit=10, offset=0)

        assert len(results) == 3
        assert all(isinstance(c, Competition) for c in results)

    def test_list_with_pagination(self, test_db):
        """ページネーション付きで一覧取得"""
        repo = CompetitionRepository(test_db)

        # 5個作成
        for i in range(5):
            comp = Competition(
                id=f"comp-{i}",
                title=f"Competition {i}",
                url=f"https://kaggle.com/c/comp-{i}",
                status="active"
            )
            repo.create(comp)

        # ページネーション
        results = repo.list(limit=2, offset=0)
        assert len(results) == 2

        results = repo.list(limit=2, offset=2)
        assert len(results) == 2

    def test_update_competition(self, test_db):
        """コンペを更新"""
        repo = CompetitionRepository(test_db)

        # 作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )
        repo.create(comp)

        # 更新
        comp.title = "Updated Competition"
        comp.summary = "New summary"
        result = repo.update(comp)

        assert result.title == "Updated Competition"
        assert result.summary == "New summary"

        # 取得して確認
        updated = repo.get_by_id("test-comp")
        assert updated.title == "Updated Competition"
        assert updated.summary == "New summary"

    def test_delete_competition(self, test_db):
        """コンペを削除"""
        repo = CompetitionRepository(test_db)

        # 作成
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )
        repo.create(comp)

        # 削除
        result = repo.delete("test-comp")
        assert result is True

        # 確認
        deleted = repo.get_by_id("test-comp")
        assert deleted is None

    def test_count_competitions(self, test_db):
        """コンペ数をカウント"""
        repo = CompetitionRepository(test_db)

        # 3個作成
        for i in range(3):
            comp = Competition(
                id=f"comp-{i}",
                title=f"Competition {i}",
                url=f"https://kaggle.com/c/comp-{i}",
                status="active"
            )
            repo.create(comp)

        count = repo.count()
        assert count == 3

    def test_list_with_filters(self, test_db):
        """フィルター付きで一覧取得"""
        repo = CompetitionRepository(test_db)

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

        # フィルター: status="active"
        results = repo.list(limit=10, offset=0, filters={"status": "active"})
        assert len(results) == 1
        assert results[0].status == "active"
