import logging
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.dependencies import get_database
from app.services.match_service import MatchService, ParseError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])

@router.post("/upload-game-report/")
async def upload_game_report(
    file: UploadFile = File(...),
    db = Depends(get_database),
):
    raw = await file.read()
    svc = MatchService(db)
    try:
        created = await svc.create_from_save(raw)
        logger.info(f"✅ Stored match {created['match_id']}")
        return created
    except ParseError:
        logger.error("🔴 Unrecognized save file format")
        raise HTTPException(status_code=400, detail="Unrecognized save file format")
    except Exception as e:
        logger.exception(f"🔴 Failed to store match: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")