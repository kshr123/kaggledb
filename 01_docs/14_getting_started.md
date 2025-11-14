# 14. 開発の始め方

## 14.1 初期セットアップ

```bash
# リポジトリクローン
git clone <repository-url>
cd kaggle-knowledge-base

# 環境変数設定
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# .env ファイルを編集してAPI Keyを設定

# Docker起動
docker-compose up -d

# DB初期化（初回のみ）
docker-compose exec backend python app/batch/init_db.py

# コンペ情報取得（初回のみ、時間かかる）
docker-compose exec backend python app/batch/fetch_competitions.py
```

## 14.2 アクセス

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 14.3 開発時のコマンド

```bash
# ログ確認
docker-compose logs -f

# コンテナ再起動
docker-compose restart

# コンテナ停止
docker-compose down

# ボリューム含めて削除
docker-compose down -v

# バックエンドのみ再ビルド
docker-compose up -d --build backend

# フロントエンドのみ再ビルド
docker-compose up -d --build frontend
```

---

**関連ドキュメント:**
- [技術スタック](./04_tech_stack.md)
- [Docker構成](./12_docker.md)
- [ルートREADME](../README.md)
