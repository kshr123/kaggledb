# 18. CORS トラブルシューティング

## 📋 CORSとは

**CORS (Cross-Origin Resource Sharing)**: ブラウザのセキュリティ機能で、異なるオリジン間のHTTPリクエストを制御する仕組み。

**オリジン**の定義:
```
プロトコル + ドメイン + ポート
```

例:
```
http://localhost:3000  ← オリジンA
http://localhost:8000  ← オリジンB（ポートが違う = 異なるオリジン）
```

---

## 🔴 よくあるCORSエラー

### 症状
- ブラウザで「データの取得に失敗しました」
- DevTools > Console に赤いエラー
- DevTools > Network タブで `CORS error` 表示

### エラーメッセージ例
```
Access to fetch at 'http://localhost:8000/api/competitions'
from origin 'http://localhost:3001' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

---

## 🛠️ 解決方法

### FastAPI (Python)

**ファイル**: `02_backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js デフォルト
        "http://localhost:3001",  # Next.js 代替ポート
        "http://localhost:5173",  # Vite デフォルト
    ],
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)
```

### 本番環境用の設定

```python
import os

# 環境変数から許可するオリジンを取得
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 必要なメソッドのみ
    allow_headers=["*"],
)
```

**環境変数** (`.env`):
```bash
# 開発環境
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# 本番環境
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

---

## 🐛 デバッグ方法

### 1. バックエンドのログ確認
リクエストが届いているか確認：
```bash
# FastAPIのログを確認
INFO:     127.0.0.1:xxxxx - "GET /api/competitions HTTP/1.1" 200 OK
```

### 2. ブラウザのDevTools確認

**Networkタブ**:
- Status が `200 OK` だがデータが取得できない → CORS問題の可能性大
- Status が `CORS error` → 確実にCORS問題

**Consoleタブ**:
- `Access to fetch ... has been blocked by CORS policy` → CORS問題

### 3. レスポンスヘッダー確認

**期待されるヘッダー**:
```
Access-Control-Allow-Origin: http://localhost:3001
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
```

### 4. プリフライトリクエスト

ブラウザは本リクエストの前に`OPTIONS`リクエスト（プリフライト）を送る場合がある：
```bash
# Networkタブで確認
OPTIONS /api/competitions  # プリフライト
GET /api/competitions       # 本リクエスト
```

両方が成功する必要がある。

---

## 📝 このプロジェクトでの対応履歴

### 発生日: 2025-11-15

**問題**:
- フロントエンド: `http://localhost:3001` で動作
- バックエンド: `http://localhost:3000` のみ許可していた
- → CORS エラー

**原因**:
Next.jsがポート3000を使おうとしたが既に使用中だったため、自動的に3001で起動。

**解決策**:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001",  # ← 追加
]
```

---

## 🔒 セキュリティ上の注意

### 開発環境
```python
# ✅ OK - 必要なオリジンのみ許可
allow_origins=["http://localhost:3000", "http://localhost:3001"]

# ❌ NG - すべてのオリジンを許可（開発時のみ）
allow_origins=["*"]  # 本番環境では絶対にNG
```

### 本番環境
```python
# ✅ 本番ドメインを明示的に指定
allow_origins=[
    "https://kaggledb.example.com",
    "https://www.kaggledb.example.com",
]

# ❌ ワイルドカード禁止
allow_origins=["*"]  # 危険！
```

---

## 🚀 ベストプラクティス

1. **環境変数で管理**: `.env` ファイルで許可するオリジンを定義
2. **最小権限の原則**: 必要なオリジン・メソッド・ヘッダーのみ許可
3. **本番では厳密に**: ワイルドカード (`*`) は使わない
4. **HTTPSを使う**: 本番環境では必ずHTTPS
5. **ログ監視**: 不正なオリジンからのリクエストを監視

---

## 🔗 関連リンク

- [MDN - CORS](https://developer.mozilla.org/ja/docs/Web/HTTP/CORS)
- [FastAPI - CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)

---

**作成日**: 2025-11-15
**最終更新**: 2025-11-15
