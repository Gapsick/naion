import json
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from database import get_db
from services.auth_service import decode_token

router = APIRouter()


@router.get("")
def get_records(authorization: str = Header(...)):
    try:
        token = authorization.removeprefix("Bearer ")
        payload = decode_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(401, "인증이 필요해요.")

    conn = get_db()
    rows = conn.execute(
        """SELECT id, conclusion, reasons_highlighted, created_at
           FROM records WHERE user_id = ?
           ORDER BY created_at DESC LIMIT 50""",
        (user_id,),
    ).fetchall()
    conn.close()

    records = [
        {
            "id": row["id"],
            "conclusion": row["conclusion"],
            "reasons_highlighted": json.loads(row["reasons_highlighted"] or "[]"),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return JSONResponse({"records": records})
