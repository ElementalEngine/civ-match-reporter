import logging
from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException
from app.dependencies import get_database
from app.services.match_service import MatchService, ParseError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["upload"])

@router.post("/upload-game-report/")
async def upload_game_report(
    file: UploadFile = File(...),
    reporter_discord_id: str = Form(...),
    is_cloud: str = Form(...),
    discord_message_id: str = Form(...),
    db = Depends(get_database),
):
    raw = await file.read()
    is_cloud_game = is_cloud == '1'
    svc = MatchService(db)
    try:
        created = await svc.create_from_save(raw, reporter_discord_id, is_cloud_game, discord_message_id)
        logger.info(f"✅ Stored match {created['match_id']}")
        return created
    except ParseError as e:
        logger.error("🔴 Unrecognized save file format")
        raise HTTPException(status_code=400, detail=f"Unrecognized save file format {e}")
    except Exception as e:
        logger.exception(f"🔴 Failed to store match: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")