from fastapi import APIRouter
from services.agent_service import session_reasons, conversations

router = APIRouter()

TEST_REASONS = [
    "발표 준비를 충분히 못 한 것 같아서",
    "남들이 나를 이상하게 볼까봐 두려워서",
    "예전에 발표하다가 실수한 기억이 있어서",
    "내가 설명을 잘 못한다는 생각이 들어서",
    "완벽하게 해야 한다는 압박이 있어서",
    "준비한 내용이 충분하지 않다고 느껴서",
]

@router.post("/seed/{session_id}")
def seed_session(session_id: str):
    """테스트용: 세션에 이유 6개 + 대화 히스토리 주입"""
    session_reasons[session_id] = TEST_REASONS.copy()
    conversations[session_id] = [
        {"role": "user", "content": "오늘 발표가 있었는데 엄청 떨렸어."},
        {"role": "assistant", "content": "많이 떨리셨군요. 왜 그렇게 떨렸던 것 같아요?"},
        {"role": "user", "content": "모르겠어. 그냥 자신이 없었나봐."},
        {"role": "assistant", "content": "자신이 없었던 이유가 뭔지 생각해본 적 있어요?"},
    ]
    return {
        "ok": True,
        "session_id": session_id,
        "reasons_count": len(TEST_REASONS),
        "reasons": TEST_REASONS
    }

@router.delete("/seed/{session_id}")
def clear_session(session_id: str):
    """테스트용: 세션 초기화"""
    session_reasons.pop(session_id, None)
    conversations.pop(session_id, None)
    return {"ok": True, "session_id": session_id}
