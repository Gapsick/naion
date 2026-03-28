import json
import os
from anthropic import AsyncAnthropic
from .tools import TOOLS
from .personas import get_system_prompt

# 비동기 Anthropic 클라이언트 (FastAPI async 환경에서 동기 클라이언트 쓰면 이벤트 루프 블로킹됨)
client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"

# 세션별 대화 히스토리 저장소 (인메모리 — 서버 재시작 시 초기화됨, 추후 Supabase로 이전)
# key: session_id, value: Claude messages 배열 [{role, content}, ...]
conversations: dict[str, list] = {}

# 세션별 이유 저장소
# key: session_id, value: 이유 문자열 리스트
session_reasons: dict[str, list[str]] = {}


def execute_tool(name: str, tool_input: dict, session_id: str) -> str:
    """
    Claude가 tool_use를 요청했을 때 실제로 실행하는 함수.
    수업 Ch3/03_tool_use_loop.py의 execute_tool() 패턴과 동일.

    반환값은 JSON 문자열 — Claude에게 tool_result로 다시 전달됨.
    """
    if name == "save_reason":
        # 사용자가 말한 이유를 세션 저장소에 추가
        reason = tool_input["reason"]
        if session_id not in session_reasons:
            session_reasons[session_id] = []
        session_reasons[session_id].append(reason)
        count = len(session_reasons[session_id])
        return json.dumps({
            "saved": reason,
            "total_count": count,
            "message": f"이유 저장 완료 ({count}/5)"
        }, ensure_ascii=False)

    elif name == "get_reasons":
        # 현재까지 저장된 이유 목록과 개수 반환
        # Claude가 "몇 개 남았는지" 파악할 때 사용
        reasons = session_reasons.get(session_id, [])
        return json.dumps({
            "reasons": reasons,
            "count": len(reasons),
            "ready_for_summary": len(reasons) >= 5  # 5개 이상이면 요약 가능
        }, ensure_ascii=False)

    elif name == "find_keywords":
        # 이유 목록을 그대로 Claude에게 돌려줌
        # 실제 키워드 추출과 결론 생성은 Claude가 담당
        reasons = tool_input.get("reasons", [])
        return json.dumps({
            "reasons": reasons,
            "instruction": "위 이유들에서 공통 키워드를 추출하여 '나는 [키워드]해서 [키워드]했었구나' 형식의 결론을 생성하세요."
        }, ensure_ascii=False)

    return json.dumps({"error": f"Unknown tool: {name}"})


def get_reason_count(session_id: str) -> int:
    """현재 세션에 저장된 이유 개수 반환"""
    return len(session_reasons.get(session_id, []))


def get_reasons_list(session_id: str) -> list[str]:
    """현재 세션에 저장된 이유 목록 반환 (summary route에서 사용)"""
    return session_reasons.get(session_id, [])


async def run_agent(message: str, session_id: str, user_id: str, persona: str, context: str | None = None):
    """
    Agent Loop — 수업 Ch3/03_tool_use_loop.py 패턴을 FastAPI + async로 포팅.

    흐름:
        while True:
            response = Claude(messages, tools)
            if stop_reason == "tool_use":
                결과 = execute_tool()
                messages에 결과 추가
                continue  ← 툴 결과를 들고 Claude 재호출
            else (stop_reason == "end_turn"):
                break  ← 최종 답변 완료

    SSE(Server-Sent Events)로 각 단계를 프론트에 실시간 전달:
        - tool_call  : Claude가 어떤 툴을 호출했는지
        - tool_result: 툴 실행 결과
        - text       : Claude의 최종 텍스트 응답
        - done       : 루프 종료 + 현재 이유 개수
    """
    # 세션 히스토리 초기화 (첫 메시지인 경우)
    if session_id not in conversations:
        conversations[session_id] = []
        # STEP 1 내용이 있으면 시스템 컨텍스트로 히스토리에 먼저 주입
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
    max_iterations = 10  # 무한 루프 방지

    for iteration in range(max_iterations):
        # Claude 호출 — 툴 목록과 전체 대화 히스토리를 함께 전달
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=history,
        )

        # ── Case 1: 최종 답변 (툴 호출 없음) ──────────────────────────
        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"
            # 히스토리에 assistant 답변 추가 (text 블록만 찾아서 저장)
            final_text = next((b.text for b in response.content if b.type == "text"), "")
            history.append({"role": "assistant", "content": final_text})
            break

        # ── Case 2: 툴 호출 요청 ──────────────────────────────────────
        if response.stop_reason == "tool_use":
            # Claude의 tool_use 블록 포함 응답을 히스토리에 추가
            history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                # 툴 호출과 함께 텍스트가 있으면 먼저 전송 (ex: "이유를 저장할게요")
                if block.type == "text" and block.text:
                    yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"

                if block.type == "tool_use":
                    # 프론트에 툴 호출 중임을 알림
                    yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name, 'input': block.input})}\n\n"

                    # 실제 툴 실행
                    result = execute_tool(block.name, block.input, session_id)

                    # 프론트에 툴 결과 전달
                    yield f"data: {json.dumps({'type': 'tool_result', 'tool': block.name, 'result': result})}\n\n"

                    # tool_result를 히스토리에 추가 → 다음 루프에서 Claude가 참고
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # Claude가 어떤 툴 호출의 결과인지 매칭
                        "content": result,
                    })

            # 모든 툴 결과를 한 번에 히스토리에 추가 후 루프 재시작
            history.append({"role": "user", "content": tool_results})

    # 루프 종료 시 현재 이유 개수를 프론트에 전달 (버튼 활성화 여부 판단용)
    reason_count = get_reason_count(session_id)
    yield f"data: {json.dumps({'type': 'done', 'reason_count': reason_count})}\n\n"
