"""
データベース初期化のテスト
TDD: Red → Green → Refactor
"""

import pytest
import sqlite3
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_db():
    """一時的なテスト用データベースを作成"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # テスト後にクリーンアップ
    if os.path.exists(path):
        os.unlink(path)


class TestDatabaseInitialization:
    """データベース初期化のテストクラス"""

    def test_create_competitions_table(self, temp_db):
        """competitionsテーブルが正しく作成されるか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # テーブルが存在することを確認
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='competitions'
        """)
        assert cursor.fetchone() is not None

        # カラムの確認
        cursor.execute("PRAGMA table_info(competitions)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {
            'id', 'title', 'url', 'start_date', 'end_date',
            'status', 'metric', 'description', 'summary',
            'tags', 'data_types', 'domain',
            'discussion_count', 'solution_status',
            'created_at', 'updated_at'
        }
        assert expected_columns.issubset(columns)

        conn.close()

    def test_create_discussions_table(self, temp_db):
        """discussionsテーブルが正しく作成されるか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='discussions'
        """)
        assert cursor.fetchone() is not None

        conn.close()

    def test_create_solutions_table(self, temp_db):
        """solutionsテーブルが正しく作成されるか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='solutions'
        """)
        assert cursor.fetchone() is not None

        conn.close()

    def test_create_tags_table(self, temp_db):
        """tagsテーブルが正しく作成されるか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='tags'
        """)
        assert cursor.fetchone() is not None

        # カラムの確認（descriptionカラムが追加されている）
        cursor.execute("PRAGMA table_info(tags)")
        columns = {row[1] for row in cursor.fetchall()}
        expected_columns = {'id', 'name', 'category', 'display_order', 'description'}
        assert expected_columns.issubset(columns)

        conn.close()

    def test_insert_initial_tags(self, temp_db):
        """初期タグデータが正しく挿入されるか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # タグ数の確認（6カテゴリ、合計60タグ）
        cursor.execute("SELECT COUNT(*) FROM tags")
        count = cursor.fetchone()[0]
        assert count == 60  # data_type:7 + task_type:8 + model_type:15 + solution_method:12 + competition_feature:9 + domain:9

        # 各カテゴリのタグ数確認
        cursor.execute("SELECT category, COUNT(*) FROM tags GROUP BY category ORDER BY category")
        category_counts = dict(cursor.fetchall())
        assert category_counts['data_type'] == 7
        assert category_counts['task_type'] == 8
        assert category_counts['model_type'] == 15
        assert category_counts['solution_method'] == 12
        assert category_counts['competition_feature'] == 9
        assert category_counts['domain'] == 9

        # 特定のタグが存在することを確認
        cursor.execute("SELECT name FROM tags WHERE name='テーブルデータ'")
        assert cursor.fetchone() is not None

        cursor.execute("SELECT name FROM tags WHERE name='不均衡データ'")
        assert cursor.fetchone() is not None

        cursor.execute("SELECT name FROM tags WHERE name='LightGBM'")
        assert cursor.fetchone() is not None

        # カテゴリの確認（6つの新しいカテゴリ）
        cursor.execute("SELECT DISTINCT category FROM tags ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        expected_categories = [
            'competition_feature',
            'data_type',
            'domain',
            'model_type',
            'solution_method',
            'task_type'
        ]
        assert sorted(categories) == sorted(expected_categories)

        conn.close()

    def test_create_indexes(self, temp_db):
        """インデックスが正しく作成されるか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # インデックスの確認
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        indexes = {row[0] for row in cursor.fetchall()}

        expected_indexes = {
            'idx_competitions_status',
            'idx_competitions_end_date',
            'idx_competitions_created_at',
            'idx_discussions_competition_id',
            'idx_discussions_votes',
            'idx_discussions_posted_at',
            'idx_solutions_competition_id',
            'idx_solutions_rank',
            'idx_tags_category'
        }

        assert expected_indexes.issubset(indexes)

        conn.close()

    def test_idempotent_initialization(self, temp_db):
        """データベース初期化を複数回実行しても安全か"""
        from app.batch.init_db import initialize_database

        # 1回目
        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tags")
        count_first = cursor.fetchone()[0]
        conn.close()

        # 2回目
        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tags")
        count_second = cursor.fetchone()[0]
        conn.close()

        # タグ数が変わらないことを確認（重複挿入されない）
        assert count_first == count_second == 60

    def test_foreign_key_constraints(self, temp_db):
        """外部キー制約が設定されているか"""
        from app.batch.init_db import initialize_database

        initialize_database(temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # discussionsテーブルの外部キー
        cursor.execute("PRAGMA foreign_key_list(discussions)")
        fk_list = cursor.fetchall()
        assert len(fk_list) > 0
        assert fk_list[0][2] == 'competitions'  # 参照先テーブル

        # solutionsテーブルの外部キー
        cursor.execute("PRAGMA foreign_key_list(solutions)")
        fk_list = cursor.fetchall()
        assert len(fk_list) > 0
        assert fk_list[0][2] == 'competitions'  # 参照先テーブル

        conn.close()
