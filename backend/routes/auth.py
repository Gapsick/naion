from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from services.auth_service import (
    register_user, login_user, update_nickname,
    create_access_token, create_refresh_token, decode_token,
)

router = APIRouter()


class AuthRequest(BaseModel):
    nickname: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register")
def register(req: AuthRequest):
    user = register_user(req.nickname, req.password)
    if not user:
        raise HTTPException(400, "이미 사용 중인 닉네임이에요.")
    return {
        "access_token":  create_access_token(user["id"]),
        "refresh_token": create_refresh_token(user["id"]),
        "user": user,
    }


@router.post("/login")
def login(req: AuthRequest):
    user = login_user(req.nickname, req.password)
    if not user:
        raise HTTPException(401, "닉네임 또는 비밀번호가 맞지 않아요.")
    return {
        "access_token":  create_access_token(user["id"]),
        "refresh_token": create_refresh_token(user["id"]),
        "user": user,
    }


@router.post("/refresh")
def refresh(req: RefreshRequest):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError
        return {"access_token": create_access_token(payload["sub"])}
    except Exception:
        raise HTTPException(401, "토큰이 만료됐거나 유효하지 않아요.")


class NicknameRequest(BaseModel):
    nickname: str


@router.patch("/nickname")
def change_nickname(req: NicknameRequest, authorization: str = Header(...)):
    try:
        token = authorization.removeprefix("Bearer ")
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "인증이 필요해요.")

    result = update_nickname(user_id, req.nickname.strip())
    if not result:
        raise HTTPException(400, "이미 사용 중인 닉네임이에요.")
    return {"user": result}


@router.get("/me")
def me(authorization: str = Header(...)):
    try:
        token = authorization.removeprefix("Bearer ")
        payload = decode_token(token)
        return {"user_id": payload["sub"]}
    except Exception:
        raise HTTPException(401, "인증이 필요해요.")
