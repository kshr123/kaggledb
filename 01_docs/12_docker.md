# 12. Docker構成

## 12.1 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: kaggle-kb-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/app
      - ./backend/data:/app/data
    environment:
      - KAGGLE_USERNAME=${KAGGLE_USERNAME}
      - KAGGLE_KEY=${KAGGLE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_PATH=/app/data/kaggle_competitions.db
      - CORS_ORIGINS=http://localhost:3000
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: kaggle-kb-frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    command: npm run dev
```

## 12.2 backend/Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# ポート公開
EXPOSE 8000

# デフォルトコマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 12.3 frontend/Dockerfile

```dockerfile
FROM node:20-slim

WORKDIR /app

# 依存関係インストール
COPY package*.json ./
RUN npm install

# アプリケーションコピー
COPY . .

# ポート公開
EXPOSE 3000

# デフォルトコマンド
CMD ["npm", "run", "dev"]
```

---

**関連ドキュメント:**
- [技術スタック](./04_tech_stack.md)
- [開発の始め方](./14_getting_started.md)
- [非機能要件](./08_non_functional_requirements.md)
