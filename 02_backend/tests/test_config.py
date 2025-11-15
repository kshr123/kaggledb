"""
config.py のテスト（TDD: Red）

config.pyが提供する設定管理機能をテストします。
"""

import pytest
import os
from pathlib import Path


class TestConfig:
    """設定管理のテスト"""

    def test_database_path_exists(self):
        """DATABASE_PATH が設定されているか"""
        from app.config import DATABASE_PATH

        assert DATABASE_PATH is not None
        assert isinstance(DATABASE_PATH, (str, Path))

    def test_database_path_is_valid(self):
        """DATABASE_PATH が有効なパスか"""
        from app.config import DATABASE_PATH

        # 'data/kaggle_competitions.db' の形式を想定
        assert 'kaggle_competitions.db' in str(DATABASE_PATH)

    def test_schema_path_exists(self):
        """SCHEMA_PATH が設定されているか"""
        from app.config import SCHEMA_PATH

        assert SCHEMA_PATH is not None
        assert isinstance(SCHEMA_PATH, (str, Path))

    def test_schema_path_is_valid(self):
        """SCHEMA_PATH が有効なパスで、ファイルが存在するか"""
        from app.config import SCHEMA_PATH

        assert 'schema.sql' in str(SCHEMA_PATH)
        assert Path(SCHEMA_PATH).exists()

    def test_kaggle_api_key_loaded(self):
        """Kaggle API キーが.envから読み込まれているか"""
        from app.config import KAGGLE_USERNAME, KAGGLE_KEY

        # 環境変数が設定されていない場合はNoneを返すべき
        # 実際に設定されている場合は文字列
        assert KAGGLE_USERNAME is None or isinstance(KAGGLE_USERNAME, str)
        assert KAGGLE_KEY is None or isinstance(KAGGLE_KEY, str)

    def test_openai_api_key_loaded(self):
        """OpenAI API キーが.envから読み込まれているか"""
        from app.config import OPENAI_API_KEY

        assert OPENAI_API_KEY is None or isinstance(OPENAI_API_KEY, str)

    def test_config_values_not_hardcoded_secrets(self):
        """設定に秘密情報がハードコードされていないか"""
        from app.config import OPENAI_API_KEY, KAGGLE_KEY
        import app.config as config_module
        import inspect

        # config.pyのソースコードを取得
        source = inspect.getsource(config_module)

        # ソースコードに直接APIキーが書かれていないことを確認
        assert 'sk-proj-' not in source, "OpenAI APIキーがハードコードされている"
        assert 'sk-' not in source or 'os.getenv' in source, "APIキーがハードコードされている可能性"

        # 環境変数から読み込まれていることを確認
        if OPENAI_API_KEY:
            assert OPENAI_API_KEY == os.getenv('OPENAI_API_KEY')

        if KAGGLE_KEY:
            assert KAGGLE_KEY == os.getenv('KAGGLE_KEY')
