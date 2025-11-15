"""
設定管理モジュール

環境変数とパス設定を管理します。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# データベース設定
DATABASE_PATH = BASE_DIR / "data" / "kaggle_competitions.db"

# スキーマファイルのパス
SCHEMA_PATH = BASE_DIR / "schema.sql"

# Kaggle API設定
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")

# OpenAI API設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# デバッグモード
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# ログレベル
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
