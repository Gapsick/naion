from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    user_id: str
    context: Optional[str] = None
    persona: Optional[str] = "warm"

class SummaryRequest(BaseModel):
    user_id: str

class Persona:
    WARM = "warm"
    FACTUAL = "factual"
    COACH = "coach"
