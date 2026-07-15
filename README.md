# Todo App (Python)

FastAPI + React + SQLite + JWT認証で作ったシンプルなTodoアプリです。

## デモ
🔗 https://to-do-app-python-eight.vercel.app

※ 無料プランのため、しばらく操作がないとサーバーが休止し、再アクセス時に起動まで30秒〜1分ほどかかることがあります。
※ 無料プランの制約上、データが定期的にリセットされる場合があります。

## 機能
- ユーザー登録・ログイン（JWT認証）
- Todoの追加・一覧表示・完了切り替え・削除
- ユーザーごとにTodoを管理

## 技術スタック
- Backend: FastAPI, SQLModel, SQLite
- Frontend: React, Vite, axios

## 起動方法

### バックエンド
\`\`\`bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
\`\`\`

### フロントエンド
\`\`\`bash
cd my-app-frontend
npm install
npm run dev
\`\`\`
