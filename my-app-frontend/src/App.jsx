import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  // ログイン状態の管理（トークンをブラウザに保存し、リロードしても残るようにする）
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authMode, setAuthMode] = useState("login"); // "login" か "register"
  const [authError, setAuthError] = useState("");

  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");

  // ログイン済みならTodoを取得
  useEffect(() => {
    if (token) {
      fetchTodos();
    }
  }, [token]);

  // --- 認証系 ---

  const handleRegister = async () => {
    setAuthError("");
    try {
      await axios.post(`${API_URL}/register`, { email, password });
      // 登録成功したら、そのままログイン処理を呼ぶ
      await handleLogin();
    } catch (err) {
      setAuthError(err.response?.data?.detail || "登録に失敗しました");
    }
  };

  const handleLogin = async () => {
    setAuthError("");
    try {
      // ログインAPIはJSONではなく、フォーム形式で送る必要がある
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);

      const res = await axios.post(`${API_URL}/login`, params);
      const newToken = res.data.access_token;

      setToken(newToken);
      localStorage.setItem("token", newToken);
    } catch (err) {
      setAuthError(err.response?.data?.detail || "ログインに失敗しました");
    }
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("token");
    setTodos([]);
  };

  // --- Todo操作系（すべてトークンを一緒に送る）---

  const authHeader = { headers: { Authorization: `Bearer ${token}` } };

  const fetchTodos = async () => {
    try {
      const res = await axios.get(`${API_URL}/todos`, authHeader);
      setTodos(res.data);
    } catch (err) {
      // トークンが無効・期限切れの場合は自動でログアウトさせる
      if (err.response?.status === 401) {
        handleLogout();
      }
    }
  };

  const addTodo = async () => {
    if (title.trim() === "") return;
    await axios.post(`${API_URL}/todos`, { title }, authHeader);
    setTitle("");
    fetchTodos();
  };

  const toggleTodo = async (id) => {
    await axios.put(`${API_URL}/todos/${id}`, {}, authHeader);
    fetchTodos();
  };

  const deleteTodo = async (id) => {
    await axios.delete(`${API_URL}/todos/${id}`, authHeader);
    fetchTodos();
  };

  // --- 画面表示 ---

  // ログインしていない場合: ログイン/登録フォームを表示
  if (!token) {
    return (
      <div className="auth-container">
        <h1>{authMode === "login" ? "ログイン" : "新規登録"}</h1>

        <input
          type="email"
          placeholder="メールアドレス"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: "0.5rem" }}
        />
        <input
          type="password"
          placeholder="パスワード"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ display: "block", width: "100%", marginBottom: "1rem" }}
        />

        {authError && <p className="auth-error">{authError}</p>}

        {authMode === "login" ? (
          <button onClick={handleLogin}>ログイン</button>
        ) : (
          <button onClick={handleRegister}>登録する</button>
        )}

        <p className="auth-switch">
          {authMode === "login" ? (
            <>
              アカウントがない場合は{" "}
              <span
                style={{ color: "blue", cursor: "pointer" }}
                onClick={() => setAuthMode("register")}
              >
                新規登録
              </span>
            </>
          ) : (
            <>
              すでにアカウントがある場合は{" "}
              <span
                style={{ color: "blue", cursor: "pointer" }}
                onClick={() => setAuthMode("login")}
              >
                ログイン
              </span>
            </>
          )}
        </p>
      </div>
    );
  }

  // ログイン済みの場合: Todoリストを表示
  return (
    <div style={{ padding: "2rem" }}>
      <div className="app-header">
        <h1>Todoリスト</h1>
        <button onClick={handleLogout}>ログアウト</button>
      </div>

      <div className="todo-form">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="新しいTodoを入力"
        />
        <button onClick={addTodo}>追加</button>
      </div>

      <ul className="todo-list">
        {todos.map((todo) => (
          <li key={todo.id} className="todo-item">
            <span
              onClick={() => toggleTodo(todo.id)}
              style={{
                textDecoration: todo.done ? "line-through" : "none",
                cursor: "pointer",
              }}
            >
              {todo.title}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>削除</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
