from fastapi import APIRouter

router = APIRouter()

@router.get("/me")
def me():
    return {"message": "auth coming soon"}
