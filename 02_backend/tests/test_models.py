"""
モデルクラスのテスト
"""
import pytest
from datetime import datetime
from app.models.competition import Competition
from app.models.discussion import Discussion
from app.models.solution import Solution
from app.models.tag import Tag


class TestCompetitionModel:
    """Competitionモデルのテスト"""

    def test_create_competition_with_required_fields(self):
        """必須フィールドのみでCompetitionを作成"""
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )

        assert comp.id == "test-comp"
        assert comp.title == "Test Competition"
        assert comp.url == "https://kaggle.com/c/test-comp"
        assert comp.status == "active"

    def test_create_competition_with_all_fields(self):
        """全フィールドでCompetitionを作成"""
        now = datetime.now()
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            start_date=now,
            end_date=now,
            status="active",
            metric="AUC",
            metric_description="Area Under Curve",
            description="Test description",
            summary="Test summary",
            tags=["NLP", "Classification"],
            data_types=["Text"],
            domain="Natural Language",
            dataset_info='{"files": []}',
            discussion_count=10,
            solution_status="未着手",
            is_favorite=False
        )

        assert comp.metric == "AUC"
        assert comp.tags == ["NLP", "Classification"]
        assert comp.discussion_count == 10

    def test_competition_to_dict(self):
        """CompetitionをDict形式に変換"""
        comp = Competition(
            id="test-comp",
            title="Test Competition",
            url="https://kaggle.com/c/test-comp",
            status="active"
        )

        comp_dict = comp.to_dict()

        assert isinstance(comp_dict, dict)
        assert comp_dict["id"] == "test-comp"
        assert comp_dict["title"] == "Test Competition"

    def test_competition_from_dict(self):
        """Dict形式からCompetitionを作成"""
        data = {
            "id": "test-comp",
            "title": "Test Competition",
            "url": "https://kaggle.com/c/test-comp",
            "status": "active",
            "metric": "AUC"
        }

        comp = Competition.from_dict(data)

        assert comp.id == "test-comp"
        assert comp.metric == "AUC"


class TestDiscussionModel:
    """Discussionモデルのテスト"""

    def test_create_discussion(self):
        """Discussionを作成"""
        disc = Discussion(
            id=1,
            competition_id="test-comp",
            title="Test Discussion",
            url="https://kaggle.com/c/test-comp/discussion/1",
            author="test_user",
            vote_count=10,
            comment_count=5
        )

        assert disc.id == 1
        assert disc.competition_id == "test-comp"
        assert disc.vote_count == 10

    def test_discussion_to_dict(self):
        """DiscussionをDict形式に変換"""
        disc = Discussion(
            id=1,
            competition_id="test-comp",
            title="Test Discussion",
            url="https://kaggle.com/c/test-comp/discussion/1",
            author="test_user",
            vote_count=10,
            comment_count=5
        )

        disc_dict = disc.to_dict()

        assert isinstance(disc_dict, dict)
        assert disc_dict["id"] == 1
        assert disc_dict["author"] == "test_user"


class TestSolutionModel:
    """Solutionモデルのテスト"""

    def test_create_solution(self):
        """Solutionを作成"""
        sol = Solution(
            id=1,
            competition_id="test-comp",
            title="1st Place Solution",
            url="https://kaggle.com/c/test-comp/discussion/100",
            author="winner",
            medal="gold",
            rank=1,
            vote_count=100,
            comment_count=20
        )

        assert sol.id == 1
        assert sol.medal == "gold"
        assert sol.rank == 1

    def test_solution_to_dict(self):
        """SolutionをDict形式に変換"""
        sol = Solution(
            id=1,
            competition_id="test-comp",
            title="1st Place Solution",
            url="https://kaggle.com/c/test-comp/discussion/100",
            author="winner",
            medal="gold",
            rank=1,
            vote_count=100,
            comment_count=20
        )

        sol_dict = sol.to_dict()

        assert isinstance(sol_dict, dict)
        assert sol_dict["medal"] == "gold"
        assert sol_dict["rank"] == 1


class TestTagModel:
    """Tagモデルのテスト"""

    def test_create_tag(self):
        """Tagを作成"""
        tag = Tag(
            name="NLP",
            category="technique",
            display_order=1
        )

        assert tag.name == "NLP"
        assert tag.category == "technique"
        assert tag.display_order == 1

    def test_tag_to_dict(self):
        """TagをDict形式に変換"""
        tag = Tag(
            name="NLP",
            category="technique",
            display_order=1
        )

        tag_dict = tag.to_dict()

        assert isinstance(tag_dict, dict)
        assert tag_dict["name"] == "NLP"
        assert tag_dict["category"] == "technique"
