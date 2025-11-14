# 11. バックエンド詳細仕様

## 11.1 FastAPI アプリケーション構造

**main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import competitions, discussions, solutions, tags

app = FastAPI(
    title="Kaggle Knowledge Base API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(competitions.router, prefix="/api/competitions", tags=["competitions"])
app.include_router(discussions.router, prefix="/api/discussions", tags=["discussions"])
app.include_router(solutions.router, prefix="/api/solutions", tags=["solutions"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])

@app.get("/")
def root():
    return {"message": "Kaggle Knowledge Base API"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

## 11.2 データベース接続（database.py）

```python
import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "data/kaggle_competitions.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

def fetch_all(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def fetch_one(query: str, params: tuple = ()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
```

## 11.3 Pydantic モデル（models.py）

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class CompetitionBase(BaseModel):
    title: str
    url: str
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    metric: Optional[str]
    summary: str
    tags: List[str]
    data_types: List[str]
    domain: str

class Competition(CompetitionBase):
    id: str
    description: Optional[str]
    discussion_count: int
    solution_status: str
    created_at: datetime
    updated_at: datetime

class CompetitionListResponse(BaseModel):
    items: List[Competition]
    total: int
    page: int
    limit: int
    total_pages: int

class UpdateTagsRequest(BaseModel):
    tags: List[str]

# その他のモデル...
```

---

**関連ドキュメント:**
- [データ設計](./03_data_design.md)
- [API設計](./07_api_design.md)
- [技術スタック](./04_tech_stack.md)
- [Docker構成](./12_docker.md)
