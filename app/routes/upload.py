import logging
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.parsers import parse_civ7_save, parse_civ6_save
from app.models.db_models import MatchModel
from app.dependencies import get_database

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])

def _try_parse(parser, data: bytes, tag: str):
    try:
        parsed = parser(data)
        parsed["game"] = tag
        logger.info(f"✅ Parsed as {tag}")
        return parsed
    except Exception as e:
        logger.warning(f"⚠️ {tag} parser failed: {e}")
        return None

@router.post("/upload-game-report/")
async def upload_game_report(
    file: UploadFile = File(...),
    db=Depends(get_database),
):
    raw = await file.read()

    parsed = _try_parse(parse_civ7_save, raw, "Civ7") or _try_parse(parse_civ6_save, raw, "Civ6")
    if not parsed:
        logger.error("🔴 Unrecognized save file format")
        raise HTTPException(status_code=400, detail="Unrecognized save file format")

    match = MatchModel(**parsed)
    result = await db.pending_matches.insert_one(match.dict())
    match_id = str(result.inserted_id)
    logger.info(f"✅ Stored match {match_id}")

    return {"match_id": match_id, **match.dict()}