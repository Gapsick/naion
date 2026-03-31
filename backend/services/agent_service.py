import json
import os
from anthropic import AsyncAnthropic
from .tools import TOOLS
from .personas import get_system_prompt

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"

# 세션별 대화 히스토리 저장소 (인메모리)
conversations: dict[str, list] = {}

# 세션별 이유 저장소 (인메모리)
session_reasons: dict[str, list[str]] = {}


def execute_tool(name: str, tool_input: dict, session_id: str) -> str:
    if name == "save_reason":
        reason = tool_input["reason"]
        if session_id not in session_reasons:
            session_reasons[session_id] = []
        session_reasons[session_id].append(reason)
        count = len(session_reasons[session_id])
        return json.dumps({
            "saved": reason,
            "total_count": count,
            "message": f"이유 저장 완료 ({count}개)"
        }, ensure_ascii=False)

    elif name == "get_reasons":
        reasons = session_reasons.get(session_id, [])
        return json.dumps({
            "reasons": reasons,
            "count": len(reasons),
        }, ensure_ascii=False)

    return json.dumps({"error": f"Unknown tool: {name}"})


def get_reasons_list(session_id: str) -> list[str]:
    """현재 세션에 저장된 이유 목록 반환 (summary route에서 사용)"""
    return session_reasons.get(session_id, [])


async def run_agent(message: str, session_id: str, user_id: str, persona: str, context: str | None = None):
    """
    Agent Loop — Claude가 tool_use를 반환하면 execute_tool()로 실행 후 재호출.

    SSE 이벤트:
        text        : Claude 텍스트 응답
        tool_call   : 툴 호출 중
        tool_result : 툴 실행 결과 (save_reason → 프론트 카운트 업데이트)
        done        : 루프 종료 + 현재 이유 개수
    """
    if session_id not in conversations:
        conversations[session_id] = []
        if context:
            conversations[session_id].append({
                "role": "user",
                "content": f"[사용자가 자유롭게 적은 내용]\n{context}"
            })
            conversations[session_id].append({
                "role": "assistant",
                "content": "내용을 잘 읽었어요. 이걸 바탕으로 질문할게요."
            })

    history = conversations[session_id]
    history.append({"role": "user", "content": message})

    system_prompt = get_system_prompt(persona)
    max_iterations = 10

    for _ in range(max_iterations):
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=history,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"
            final_text = next((b.text for b in response.content if b.type == "text"), "")
            history.append({"role": "assistant", "content": final_text})
            break

        if response.stop_reason == "tool_use":
            history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "text" and block.text:
                    yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"

                if block.type == "tool_use":
                    yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name, 'input': block.input})}\n\n"

                    result = execute_tool(block.name, block.input, session_id)

                    yield f"data: {json.dumps({'type': 'tool_result', 'tool': block.name, 'result': result})}\n\n"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            history.append({"role": "user", "content": tool_results})

    reason_count = len(session_reasons.get(session_id, []))
    yield f"data: {json.dumps({'type': 'done', 'reason_count': reason_count})}\n\n"
