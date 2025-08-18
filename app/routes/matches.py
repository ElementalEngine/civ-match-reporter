import logging
from fastapi import APIRouter, Depends, HTTPException, Form
from app.dependencies import get_database
from app.models.schemas import MatchResponse, MatchUpdate
from app.services.match_service import MatchService, InvalidIDError, NotFoundError, MatchServiceError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/get-match/", response_model=MatchResponse)
async def get_match(match_id: str = Form(), db = Depends(get_database)):
    svc = MatchService(db)
    try:
        return await svc.get(match_id)
    except InvalidIDError:
        logger.error(f"🔴 Invalid match ID: {match_id}")
        raise HTTPException(status_code=400, detail="Invalid match ID")
    except NotFoundError:
        logger.warning(f"🔴 Match not found: {match_id}")
        raise HTTPException(status_code=404, detail="Match not found")

@router.put("/update-match/", response_model=MatchResponse)
async def update_match(payload: MatchUpdate = Form(), db = Depends(get_database)):
    svc = MatchService(db)
    match_id = payload.match_id
    try:
        return await svc.update(match_id, payload.dict(exclude_unset=True))
    except InvalidIDError:
        logger.error(f"🔴 Invalid match ID: {match_id}")
        raise HTTPException(status_code=400, detail="Invalid match ID")
    except NotFoundError:
        logger.warning(f"🔴 Match not found: {match_id}")
        raise HTTPException(status_code=404, detail="Match not found")
    except MatchServiceError as e:
        logger.warning(f"⚠️ Update error: {e}")
        raise HTTPException(status_code=400, detail=str(e))