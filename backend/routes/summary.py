import json
import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from anthropic import AsyncAnthropic
from models.schemas import SummaryRequest
from services.agent_service import get_reasons_list
from database import get_db

router = APIRouter()
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5-20250929"


@router.post("")
async def summary(req: SummaryRequest):
    reasons = get_reasons_list(req.session_id)
    if not reasons:
        return JSONResponse({"conclusion": "아직 저장된 이유가 없어요.", "reasons_highlighted": []})

    reasons_json = json.dumps(reasons, ensure_ascii=False)

    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="당신은 감정 패턴 분석기입니다. 반드시 JSON만 출력합니다. 마크다운이나 다른 텍스트 없이 JSON만.",
        messages=[{
            "role": "user",
            "content": f"""아래 이유 목록을 분석해줘:
{reasons_json}

아래 JSON 형식으로만 답해줘:
{{
  "conclusion": "나는 ~~ 할때 ~~ 을 느낀다 형식의 핵심 문장 1개",
  "reasons_highlighted": [
    "이유1 텍스트 (공통 핵심 단어/구에 <mark> 태그 감싸기)",
    "이유2 텍스트 (공통 핵심 단어/구에 <mark> 태그 감싸기)",
    ...
  ]
}}

규칙:
- conclusion은 "나는 ~~ 할때 ~~ 을 느낀다" 형식으로 1문장
- reasons_highlighted는 원본 이유 목록과 순서/개수 동일하게
- 이유들의 공통 패턴을 관통하는 단어/구에만 <mark> 태그 사용 (1~3개 정도)
- 공통점이 없는 이유는 태그 없이 원문 그대로
- JSON 외 다른 텍스트 절대 금지"""
        }],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    conclusion = data.get("conclusion", "")
    reasons_highlighted = data.get("reasons_highlighted", reasons)

    # DB에 기록 저장
    conn = get_db()
    conn.execute(
        "INSERT INTO records (user_id, session_id, conclusion, reasons_highlighted) VALUES (?, ?, ?, ?)",
        (req.user_id, req.session_id, conclusion, json.dumps(reasons_highlighted, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()

    return JSONResponse({
        "conclusion": conclusion,
        "reasons_highlighted": reasons_highlighted,
    })
