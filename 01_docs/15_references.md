# 15. 参考情報

## 15.1 公式ドキュメント

**Kaggle API**
- https://github.com/Kaggle/kaggle-api
- https://www.kaggle.com/docs/api

**OpenAI API**
- https://platform.openai.com/docs

**FastAPI**
- https://fastapi.tiangolo.com/

**Next.js**
- https://nextjs.org/docs

**Playwright**
- https://playwright.dev/python/

**TypeScript**
- https://www.typescriptlang.org/docs/

**Tailwind CSS**
- https://tailwindcss.com/docs

## 15.2 学習リソース

**Next.js + TypeScript**
- Next.js 公式チュートリアル
- TypeScript Handbook

**FastAPI**
- FastAPI 公式チュートリアル
- Real Python - FastAPI Guide

**Docker**
- Docker 公式ドキュメント
- Docker Compose リファレンス

---

# 付録A: 画面遷移図

```
[ホーム画面] (/)
    ├→ [コンペ詳細画面] (/competitions/[id])
    │    ├→ 基本情報セクション
    │    ├→ ディスカッションセクション
    │    └→ 上位解法セクション
    │
    └→ 外部リンク
         └→ Kaggle コンペページ
```

# 付録B: データフロー図

```
[初期セットアップ]
Kaggle API → FastAPI → LLM処理 → SQLite

[ユーザー操作]
Next.js → FastAPI → SQLite
       ← JSON     ←

[バッチ処理（日次）]
Cron → FastAPI → Kaggle API → LLM処理 → SQLite
```

# 付録C: 用語集

- **コンペ**: Kaggleコンペティション
- **ディスカッション**: Kaggleコンペのフォーラム投稿
- **解法**: コンペ終了後に公開される上位者の手法
- **Vote**: ディスカッションのいいね数
- **LLM**: Large Language Model（GPT-4o miniなど）
- **SPA**: Single Page Application
- **SSR**: Server Side Rendering
- **App Router**: Next.js 14+ の新しいルーティングシステム

---

**文書バージョン**: 2.0  
**最終更新日**: 2025-11-15
**作成者**: daisakura  
**変更履歴**:
- v2.0: Next.js + TypeScript 構成に変更、Docker対応、詳細仕様追加、ドキュメント分割
- v1.0: 初版（FastAPI + 素のJS構成）
