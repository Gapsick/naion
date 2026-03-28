from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str
    context: Optional[str] = None  # STEP 1에서 자유롭게 입력한 내용

class SummaryRequest(BaseModel):
    session_id: str
    user_id: str

class Persona:
    WARM = "warm"
    FACTUAL = "factual"
    COACH = "coach"
