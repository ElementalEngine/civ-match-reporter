import logging
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException

from app.config import settings
from app.db import init_db
from app.dependencies import get_database
from app.parsers import civ6, civ7
from app.models.db_models import MatchModel

logger = logging.getLogger(__name__)
app = FastAPI(
    title="Civ Match Reporter API",
    version=settings.civ_save_parser_version
)

# Initialize MongoDB lifecycle
init_db(app)


def try_parse_save(parser_func, data: bytes, game_tag: str):
    try:
        result = parser_func(data)
        result["game"] = game_tag
        logger.info(f"✅ Parsed as {game_tag}")
        return result
    except Exception as e:
        logger.warning(f"⚠️ Parser {game_tag} failed: {e}")
        return None


@app.get("/", tags=["health"])
async def root():
    return {"status": "🟢 OK"}


@app.post("/upload-game-report/", tags=["upload"])
async def upload_game_report(
    file: UploadFile = File(...),
    db   = Depends(get_database)
):
    raw_bytes = await file.read()

    parsed = (
        try_parse_save(civ7.parse_civ7_save, raw_bytes, "Civ7")
        or try_parse_save(civ6.parse_civ6_save, raw_bytes, "Civ6")
    )
    if not parsed:
        logger.error("🔴 Unrecognized save file format")
        raise HTTPException(status_code=400, detail="🔴 Unrecognized save file format")

    match = MatchModel(**parsed)
    insert_result = await db.pending_matches.insert_one(match.dict())
    match_id = str(insert_result.inserted_id)
    logger.info(f"✅ Stored match {match_id}")

    return {"match_id": match_id, **match.dict()}