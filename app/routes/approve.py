from fastapi import APIRouter
from app.config import CONFIRMED_PLACEMENTS, MATCH_STORAGE, MATCH_FLAGS, RATINGS
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/")
def approve():
    now = datetime.utcnow()
    approved = []
    for match_id, entry in CONFIRMED_PLACEMENTS.items():
        if entry.get("flagged"):
            continue
        if (now - entry["timestamp"]) < timedelta(hours=48):
            continue

        # Dummy rating update
        match = MATCH_STORAGE.get(match_id)
        players = match.get("players", [])
        for i, p in enumerate(players):
            pid = p["steam_id"]
            RATINGS[pid] = RATINGS.get(pid, 1000) + (10 - i * 2)  # Simplified rating logic
        approved.append(match_id)

    return {"approved_matches": approved}