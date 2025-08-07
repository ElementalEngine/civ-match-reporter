import logging
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.dependencies import get_database
from app.models.schemas import MatchResponse, MatchUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str, db=Depends(get_database)):
    try:
        oid = ObjectId(match_id)
    except Exception:
        logger.error(f"🔴 Invalid match ID: {match_id}")
        raise HTTPException(status_code=400, detail="Invalid match ID")

    doc = await db.pending_matches.find_one({"_id": oid})
    if not doc:
        logger.warning(f"🔴 Match not found: {match_id}")
        raise HTTPException(status_code=404, detail="Match not found")

    doc["_id"] = str(doc["_id"])
    return doc

@router.put("/{match_id}", response_model=MatchResponse)
async def update_match(match_id: str, payload: MatchUpdate, db=Depends(get_database)):
    try:
        oid = ObjectId(match_id)
    except Exception:
        logger.error(f"🔴 Invalid match ID: {match_id}")
        raise HTTPException(status_code=400, detail="Invalid match ID")

    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        logger.warning("⚠️ Empty update payload")
        raise HTTPException(status_code=400, detail="Empty update payload")

    res = await db.pending_matches.update_one({"_id": oid}, {"$set": update_data})
    if res.matched_count == 0:
        logger.warning(f"🔴 Match not found: {match_id}")
        raise HTTPException(status_code=404, detail="Match not found")

    doc = await db.pending_matches.find_one({"_id": oid})
    doc["_id"] = str(doc["_id"])
    logger.info(f"✅ Updated match {match_id}")
    return doc