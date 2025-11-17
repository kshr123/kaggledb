"""
DiscussionRepository と SolutionRepository のテスト
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from app.database import Database
from app.repositories.discussion import DiscussionRepository
from app.repositories.solution import SolutionRepository
from app.models.competition import Competition
from app.models.discussion import Discussion
from app.models.solution import Solution


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
        cursor.execute("""
            CREATE TABLE discussions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition_id TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                author_tier TEXT,
                tier_color TEXT,
                url TEXT NOT NULL,
                vote_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                category TEXT,
                is_pinned BOOLEAN DEFAULT 0,
                content TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competition_id) REFERENCES competitions(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition_id TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                author_tier TEXT,
                tier_color TEXT,
                url TEXT NOT NULL,
                type TEXT DEFAULT 'discussion',
                medal TEXT,
                rank INTEGER,
                vote_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                content TEXT,
                summary TEXT,
                techniques TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competition_id) REFERENCES competitions(id)
            )
        """)
        conn.commit()

    yield db

    # クリーンアップ
    Path(db_path).unlink(missing_ok=True)


class TestDiscussionRepository:
    """DiscussionRepositoryのテスト"""

    def test_create_discussion(self, test_db):
        """ディスカッションを作成"""
        repo = DiscussionRepository(test_db)

        discussion = Discussion(
            id=0,  # AUTO_INCREMENT
            competition_id="test-comp",
            title="Test Discussion",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/123",
            vote_count=10,
            comment_count=5,
            category="General Discussion",
            is_pinned=False
        )

        result = repo.create(discussion)
        assert result.id > 0
        assert result.title == "Test Discussion"

    def test_get_by_id(self, test_db):
        """IDでディスカッションを取得"""
        repo = DiscussionRepository(test_db)

        discussion = Discussion(
            id=0,
            competition_id="test-comp",
            title="Test Discussion",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/123",
            vote_count=10,
            comment_count=5
        )
        created = repo.create(discussion)

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id
        assert result.title == "Test Discussion"

    def test_list_by_competition(self, test_db):
        """コンペティションIDでディスカッション一覧を取得"""
        repo = DiscussionRepository(test_db)

        # 複数のディスカッションを作成
        for i in range(3):
            repo.create(Discussion(
                id=0,
                competition_id="test-comp",
                title=f"Discussion {i}",
                author="test-user",
                url=f"https://kaggle.com/c/test-comp/discussion/{i}",
                vote_count=i * 10,
                comment_count=i * 5
            ))

        results = repo.list_by_competition(
            competition_id="test-comp",
            sort_by="vote_count",
            order="desc"
        )

        assert len(results) == 3
        # ソート確認: vote_count降順
        assert results[0].vote_count >= results[1].vote_count

    def test_list_with_pinned_priority(self, test_db):
        """ピン留めディスカッションが優先されることを確認"""
        repo = DiscussionRepository(test_db)

        # 通常のディスカッション
        repo.create(Discussion(
            id=0,
            competition_id="test-comp",
            title="Normal Discussion",
            author="user1",
            url="https://kaggle.com/c/test-comp/discussion/1",
            vote_count=100,
            comment_count=50,
            is_pinned=False
        ))

        # ピン留めディスカッション（vote_countは低い）
        repo.create(Discussion(
            id=0,
            competition_id="test-comp",
            title="Pinned Discussion",
            author="user2",
            url="https://kaggle.com/c/test-comp/discussion/2",
            vote_count=10,
            comment_count=5,
            is_pinned=True
        ))

        results = repo.list_by_competition(
            competition_id="test-comp",
            sort_by="vote_count",
            order="desc"
        )

        # ピン留めが最初に来る
        assert results[0].is_pinned is True
        assert results[0].title == "Pinned Discussion"

    def test_update_discussion(self, test_db):
        """ディスカッションを更新"""
        repo = DiscussionRepository(test_db)

        discussion = Discussion(
            id=0,
            competition_id="test-comp",
            title="Original Title",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/123",
            vote_count=10,
            comment_count=5
        )
        created = repo.create(discussion)

        # 更新
        created.title = "Updated Title"
        created.vote_count = 20
        result = repo.update(created)

        assert result.title == "Updated Title"
        assert result.vote_count == 20

    def test_delete_discussion(self, test_db):
        """ディスカッションを削除"""
        repo = DiscussionRepository(test_db)

        discussion = Discussion(
            id=0,
            competition_id="test-comp",
            title="Test Discussion",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/123",
            vote_count=10,
            comment_count=5
        )
        created = repo.create(discussion)

        # 削除
        result = repo.delete(created.id)
        assert result is True

        # 確認
        deleted = repo.get_by_id(created.id)
        assert deleted is None

    def test_upsert_by_url(self, test_db):
        """URLで既存チェックしてinsert/updateを行う"""
        repo = DiscussionRepository(test_db)

        discussion = Discussion(
            id=0,
            competition_id="test-comp",
            title="Test Discussion",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/123",
            vote_count=10,
            comment_count=5
        )

        # 初回: insert
        created = repo.upsert_by_url(discussion)
        assert created.id > 0

        # 2回目: update (同じURL)
        discussion.vote_count = 20
        updated = repo.upsert_by_url(discussion)
        assert updated.id == created.id
        assert updated.vote_count == 20


class TestSolutionRepository:
    """SolutionRepositoryのテスト"""

    def test_create_solution(self, test_db):
        """解法を作成"""
        repo = SolutionRepository(test_db)

        solution = Solution(
            id=0,
            competition_id="test-comp",
            title="1st Place Solution",
            author="kaggle-master",
            url="https://kaggle.com/c/test-comp/discussion/456",
            vote_count=100,
            comment_count=20,
            type="discussion",
            medal="gold",
            rank=1
        )

        result = repo.create(solution)
        assert result.id > 0
        assert result.medal == "gold"
        assert result.rank == 1

    def test_get_by_id(self, test_db):
        """IDで解法を取得"""
        repo = SolutionRepository(test_db)

        solution = Solution(
            id=0,
            competition_id="test-comp",
            title="Test Solution",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/456",
            vote_count=50,
            comment_count=10
        )
        created = repo.create(solution)

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_list_by_competition_with_rank_sort(self, test_db):
        """rankでソート（NULL は最後）"""
        repo = SolutionRepository(test_db)

        # rank付きの解法
        repo.create(Solution(
            id=0,
            competition_id="test-comp",
            title="2nd Place",
            author="user1",
            url="https://kaggle.com/c/test-comp/discussion/1",
            vote_count=80,
            comment_count=15,
            rank=2
        ))

        repo.create(Solution(
            id=0,
            competition_id="test-comp",
            title="1st Place",
            author="user2",
            url="https://kaggle.com/c/test-comp/discussion/2",
            vote_count=100,
            comment_count=20,
            rank=1
        ))

        # rankなしの解法
        repo.create(Solution(
            id=0,
            competition_id="test-comp",
            title="Unranked Solution",
            author="user3",
            url="https://kaggle.com/c/test-comp/discussion/3",
            vote_count=200,
            comment_count=50,
            rank=None
        ))

        results = repo.list_by_competition(
            competition_id="test-comp",
            sort_by="rank",
            order="asc"
        )

        assert len(results) == 3
        # rank順: 1, 2, NULL
        assert results[0].rank == 1
        assert results[1].rank == 2
        assert results[2].rank is None

    def test_update_solution(self, test_db):
        """解法を更新"""
        repo = SolutionRepository(test_db)

        solution = Solution(
            id=0,
            competition_id="test-comp",
            title="Solution Draft",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/456",
            vote_count=10,
            comment_count=2
        )
        created = repo.create(solution)

        # AI分析結果を追加
        created.summary = "This solution uses XGBoost..."
        created.techniques = '{"model": "XGBoost", "features": ["fe1", "fe2"]}'
        result = repo.update(created)

        assert result.summary == "This solution uses XGBoost..."
        assert result.techniques is not None

    def test_delete_solution(self, test_db):
        """解法を削除"""
        repo = SolutionRepository(test_db)

        solution = Solution(
            id=0,
            competition_id="test-comp",
            title="Test Solution",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/456",
            vote_count=50,
            comment_count=10
        )
        created = repo.create(solution)

        # 削除
        result = repo.delete(created.id)
        assert result is True

        # 確認
        deleted = repo.get_by_id(created.id)
        assert deleted is None

    def test_upsert_by_url(self, test_db):
        """URLで既存チェックしてinsert/updateを行う"""
        repo = SolutionRepository(test_db)

        solution = Solution(
            id=0,
            competition_id="test-comp",
            title="Test Solution",
            author="test-user",
            url="https://kaggle.com/c/test-comp/discussion/456",
            vote_count=50,
            comment_count=10
        )

        # 初回: insert
        created = repo.upsert_by_url(solution)
        assert created.id > 0

        # 2回目: update (同じURL)
        solution.vote_count = 100
        solution.summary = "AI generated summary"
        updated = repo.upsert_by_url(solution)
        assert updated.id == created.id
        assert updated.vote_count == 100
        assert updated.summary == "AI generated summary"
