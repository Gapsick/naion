import json
import os
from anthropic import AsyncAnthropic
from tavily import AsyncTavilyClient
from .tools import TOOLS
from .personas import get_system_prompt
from .exceptions import ToolInputError, ToolExecutionError  # noqa: F401

tavily = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"

# 세션별 대화 히스토리 저장소 (인메모리)
conversations: dict[str, list] = {}

# 세션별 이유 저장소 (인메모리)
session_reasons: dict[str, list[str]] = {}


async def execute_tool(name: str, tool_input: dict, user_id: str) -> str:
    if name == "web_search":
        try:
            query = str(tool_input["query"])
        except (KeyError, TypeError):
            raise ToolInputError("query 값이 없거나 잘못됨")
        try:
            result = await tavily.search(query, include_answer=True, max_results=3)
            return json.dumps({
                "answer": result.get("answer", ""),
                "results": [
                    {"title": r["title"], "content": r["content"]}
                    for r in result.get("results", [])
                ]
            }, ensure_ascii=False)
        except Exception as e:
            raise ToolExecutionError(f"검색 실패: {e}")

    elif name == "save_reason":
        try:
            reason = str(tool_input["reason"])
        except (KeyError, TypeError):
            raise ToolInputError("reason 값이 없거나 잘못됨")
        if not reason:
            raise ToolInputError("reason이 빈 문자열")
        if user_id not in session_reasons:
            session_reasons[user_id] = []
        session_reasons[user_id].append(reason)
        count = len(session_reasons[user_id])
        return json.dumps({
            "saved": reason,
            "total_count": count,
            "message": f"이유 저장 완료 ({count}개)"
        }, ensure_ascii=False)

    elif name == "get_reasons":
        reasons = session_reasons.get(user_id, [])
        return json.dumps({
            "reasons": reasons,
            "count": len(reasons),
        }, ensure_ascii=False)

    raise ToolInputError(f"알 수 없는 툴: {name}")


def get_reasons_list(user_id: str) -> list[str]:
    """현재 세션에 저장된 이유 목록 반환 (summary route에서 사용)"""
    return session_reasons.get(user_id, [])


async def run_agent(message: str, user_id: str, persona: str, context: str | None = None):
    """
    Agent Loop — Claude가 tool_use를 반환하면 execute_tool()로 실행 후 재호출.

    SSE 이벤트:
        text        : Claude 텍스트 응답
        tool_call   : 툴 호출 중
        tool_result : 툴 실행 결과 (save_reason → 프론트 카운트 업데이트)
        done        : 루프 종료 + 현재 이유 개수
    """
    if user_id not in conversations:
        conversations[user_id] = []
        if context:
            conversations[user_id].append({
                "role": "user",
                "content": f"[사용자가 자유롭게 적은 내용]\n{context}"
            })
            conversations[user_id].append({
                "role": "assistant",
                "content": "내용을 잘 읽었어요. 이걸 바탕으로 질문할게요."
            })

    history = conversations[user_id]
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

                    try:
                        result = await execute_tool(block.name, block.input, user_id)
                    except ToolInputError as e:
                        # Claude한테 에러 알려줌 → 재시도 유도
                        result = json.dumps({"error": str(e)}, ensure_ascii=False)
                    except ToolExecutionError as e:
                        # 복구 불가 에러 → 프론트에 알리고 루프 종료
                        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                        return

                    yield f"data: {json.dumps({'type': 'tool_result', 'tool': block.name, 'result': result})}\n\n"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            history.append({"role": "user", "content": tool_results})

    reason_count = len(session_reasons.get(user_id, []))
    yield f"data: {json.dumps({'type': 'done', 'reason_count': reason_count})}\n\n"
