"""
FastAPI メインアプリケーション

KaggleDB のバックエンドAPIエントリーポイント
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# アプリケーション初期化
app = FastAPI(
    title="KaggleDB API",
    description="Kaggle Competition Knowledge Base API",
    version="0.1.0"
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js デフォルトポート
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
from app.routers import tags

app.include_router(tags.router, prefix="/api", tags=["tags"])


@app.get("/")
def root():
    """ルートエンドポイント"""
    return {
        "message": "Welcome to KaggleDB API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}
