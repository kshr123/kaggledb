# 12. Docker構成

## 📝 重要: Phase別の導入計画

- **Phase 1（現在）**: ローカル開発（Docker不要）
- **Phase 2以降**: Docker導入（PostgreSQL + Redis）

## 12.1 docker-compose.yml（Phase 2以降）

```yaml
version: '3.8'

services:
  # PostgreSQL データベース
  postgres:
    image: postgres:16-alpine
    container_name: kaggledb-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-kaggledb}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}
      - POSTGRES_DB=${POSTGRES_DB:-kaggledb}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./02_backend/migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kaggledb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - kaggledb-network

  # Redis キャッシュ
  redis:
    image: redis:7-alpine
    container_name: kaggledb-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - kaggledb-network

  # バックエンド API
  backend:
    build:
      context: ./02_backend
      dockerfile: Dockerfile
    container_name: kaggledb-backend
    ports:
      - "8000:8000"
    volumes:
      - ./02_backend/app:/app/app
      - ./02_backend/data:/app/data
    environment:
      - KAGGLE_USERNAME=${KAGGLE_USERNAME}
      - KAGGLE_KEY=${KAGGLE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER:-kaggledb}:${POSTGRES_PASSWORD:-password}@postgres:5432/${POSTGRES_DB:-kaggledb}
      - REDIS_URL=redis://redis:6379/0
      - REDIS_CACHE_TTL=${REDIS_CACHE_TTL:-3600}
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - kaggledb-network

  # フロントエンド
  frontend:
    build:
      context: ./03_frontend
      dockerfile: Dockerfile
    container_name: kaggledb-frontend
    ports:
      - "3000:3000"
    volumes:
      - ./03_frontend/app:/app/app
      - ./03_frontend/components:/app/components
      - ./03_frontend/lib:/app/lib
      - ./03_frontend/types:/app/types
      - ./03_frontend/public:/app/public
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    command: npm run dev
    networks:
      - kaggledb-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  kaggledb-network:
    driver: bridge
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
