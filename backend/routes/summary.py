import json
import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from anthropic import AsyncAnthropic
from models.schemas import SummaryRequest
from services.agent_service import get_reasons_list

router = APIRouter()
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"


async def stream_summary(session_id: str, user_id: str):
    reasons = get_reasons_list(session_id)
    if len(reasons) < 5:
        yield f"data: {json.dumps({'type': 'text', 'content': '이유가 5개 미만입니다.'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    reasons_text = "\n".join(f"- {r}" for r in reasons)

    response = await client.messages.create(
        model=MODEL,
        max_tokens=512,
        system="당신은 감정 패턴 분석기입니다. 이유 목록에서 본질을 꿰뚫는 핵심 문장 딱 1개만 출력합니다. 절대 2문장 이상 쓰지 않습니다. 설명, 서론, 질문 없이 결론 문장 1개만.",
        messages=[{
            "role": "user",
            "content": f"""아래는 사용자가 말한 이유 목록이야:
{reasons_text}

이유들을 하나로 꿰뚫는 핵심 문장 1개만 만들어줘.

규칙:
- "나는 ~~ 할때 ~~ 을 느낀다" 형식으로 딱 1문장
- 여러 이유를 억지로 나열하지 말고, 공통된 본질 하나만
- 문장 1개만 출력해. 설명, 번호, 서론, 질문 없이."""
        }],
    )

    for block in response.content:
        if block.type == "text":
            yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@router.post("")
async def summary(req: SummaryRequest):
    return StreamingResponse(
        stream_summary(req.session_id, req.user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
