import logging
from fastapi import FastAPI
from app.config import settings
from app.db import init_db
from app.routes import router as api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Civ Match Reporter API",
    version=settings.civ_save_parser_version,
)

init_db(app)
app.include_router(api_router)

@app.get("/", tags=["health"])
async def root():
    return {"status": "🟢 OK"}