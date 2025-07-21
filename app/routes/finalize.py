from fastapi import APIRouter, Body
from app.config import MATCH_STORAGE, CONFIRMED_PLACEMENTS

router = APIRouter()

@router.post("/")
def finalize(match_id: str = Body(...), placements: dict = Body(...)):
    if match_id not in MATCH_STORAGE:
        return {"error": "match not found"}
    CONFIRMED_PLACEMENTS[match_id] = {
        "placements": placements,
        "timestamp": __import__('datetime').datetime.utcnow(),
        "flagged": False
    }
    return {"status": "placement confirmed", "match_id": match_id}
