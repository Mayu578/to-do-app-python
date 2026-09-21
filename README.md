# Todo App (Python)

FastAPI + React + PostgreSQL(Neon) + JWT認証で作ったシンプルなTodoアプリです。

## デモ
🔗 https://to-do-app-python-eight.vercel.app

※ 無料プランのため、しばらく操作がないとサーバーが休止し、再アクセス時に起動まで30秒〜1分ほどかかることがあります。

## 機能
- ユーザー登録・ログイン（JWT認証）
- Todoの追加・一覧表示・完了切り替え・削除
- ユーザーごとにTodoを管理

## 技術スタック
- Backend: FastAPI, SQLModel, PostgreSQL (Neon)
- Frontend: React, Vite, axios(API通信)

## 起動方法

### バックエンド
  ### バックエンド
  \`\`\`bash
  source venv/bin/activate
  pip install -r requirements.txt
## .envファイルにDATABASE_URLを設定するとPostgres(Neon)に接続されます
## 未設定の場合はローカルのSQLite(todos.db)が使われます
  uvicorn main:app --reload
  \`\`\`

### フロントエンド
\`\`\`bash
cd my-app-frontend
npm install
npm run dev
\`\`\`

## 制作目的
 
React と Python(FastAPI)の学習を目的に作成したアプリです。CRUD操作とJWT認証という基本的な機能のみを実装したシンプルな構成にしています。