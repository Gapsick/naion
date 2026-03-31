import os
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt as _bcrypt
from jose import jwt
from database import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "naion-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE  = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt(rounds=4)).decode()


def verify_password(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode(), hashed.encode())


def _create_token(data: dict, expires: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: str) -> str:
    return _create_token({"sub": user_id, "type": "access"}, ACCESS_TOKEN_EXPIRE)


def create_refresh_token(user_id: str) -> str:
    return _create_token({"sub": user_id, "type": "refresh"}, REFRESH_TOKEN_EXPIRE)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def register_user(nickname: str, password: str) -> dict | None:
    """닉네임 중복 확인 후 유저 생성. 중복이면 None 반환."""
    conn = get_db()
    exists = conn.execute(
        "SELECT id FROM users WHERE nickname = ?", (nickname,)
    ).fetchone()
    if exists:
        conn.close()
        return None
    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users (id, nickname, hashed_password) VALUES (?, ?, ?)",
        (user_id, nickname, hash_password(password)),
    )
    conn.commit()
    conn.close()
    return {"id": user_id, "nickname": nickname}


def login_user(nickname: str, password: str) -> dict | None:
    """닉네임 + 비밀번호 검증. 실패하면 None 반환."""
    conn = get_db()
    row = conn.execute(
        "SELECT id, hashed_password FROM users WHERE nickname = ?", (nickname,)
    ).fetchone()
    conn.close()
    if not row or not verify_password(password, row["hashed_password"]):
        return None
    return {"id": row["id"], "nickname": nickname}
