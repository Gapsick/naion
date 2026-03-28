from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
from services.agent_service import run_agent

router = APIRouter()

@router.post("")
async def chat(req: ChatRequest):
    return StreamingResponse(
        run_agent(req.message, req.session_id, req.user_id, "warm", req.context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
