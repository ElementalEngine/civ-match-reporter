from fastapi import APIRouter, Body
from app.config import MATCH_FLAGS, CONFIRMED_PLACEMENTS

router = APIRouter()

@router.post("/")
def flag(match_id: str = Body(...)):
    if match_id in CONFIRMED_PLACEMENTS:
        CONFIRMED_PLACEMENTS[match_id]["flagged"] = True
        MATCH_FLAGS[match_id] = True
        return {"status": "match flagged"}
    return {"error": "cannot flag unconfirmed match"}
