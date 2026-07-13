from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

import os

origins = [
    "http://localhost:5173",
    os.environ.get("FRONTEND_URL", ""),  # Renderで環境変数として設定します
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- パスワードのハッシュ化 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT関連の設定 ---
SECRET_KEY = os.environ.get("SECRET_KEY", "this-is-a-secret-key-change-later")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- トークンをどこから受け取るかの設定（/login のURLを指定）---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- データベースの設定 ---
DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(DATABASE_URL, echo=True)

# --- テーブル定義 ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

class UserCreate(SQLModel):
    email: str
    password: str

class UserRead(SQLModel):
    id: int
    email: str

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    done: bool = False
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class TodoCreate(SQLModel):
    title: str

# --- アプリ起動時にテーブルを作成 ---
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Hello from Python!"}

# --- ユーザー登録 ---
@app.post("/register", response_model=UserRead)
def register(user: UserCreate):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == user.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = pwd_context.hash(user.password)
        new_user = User(email=user.email, hashed_password=hashed_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

# --- トークンを作る関数 ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- ログイン ---
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == form_data.username)).first()

        if not user or not pwd_context.verify(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

# --- 「今リクエストしてきているのは誰か」を確認する関数 ---
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user is None:
            raise credentials_exception
        return user

# 1. 全件取得（自分のTodoだけ）
@app.get("/todos", response_model=List[Todo])
def get_todos(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
        return todos

# 2. 追加（自分のTodoとして作成）
@app.post("/todos", response_model=Todo)
def create_todo(todo: TodoCreate, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        new_todo = Todo(title=todo.title, done=False, user_id=current_user.id)
        session.add(new_todo)
        session.commit()
        session.refresh(new_todo)
        return new_todo

# 3. 完了/未完了の切り替え（自分のTodoのみ）
@app.put("/todos/{todo_id}", response_model=Todo)
def toggle_todo(todo_id: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo or todo.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Todo not found")
        todo.done = not todo.done
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

# 4. 削除（自分のTodoのみ）
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo or todo.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Todo not found")
        session.delete(todo)
        session.commit()
        return {"message": "deleted"}
