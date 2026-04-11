from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from models.schemas import ChatRequest
from services.agent_service import run_agent, conversations, session_reasons
from services.auth_service import decode_token

router = APIRouter()

@router.post("")
async def chat(req: ChatRequest):
    return StreamingResponse(
        run_agent(req.message, req.user_id, req.persona or "warm", req.context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

@router.delete("")
async def reset_chat(authorization: str = Header(...)):
    try:
        token = authorization.removeprefix("Bearer ")
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "인증이 필요해요.")

    conversations.pop(user_id, None)
    session_reasons.pop(user_id, None)
    return JSONResponse({"ok": True})
