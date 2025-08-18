import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.db import db_lifespan
from app.dependencies import get_database

from app.routes import router

logger = logging.getLogger(__name__)

app = FastAPI(title="Civ Save Tool", lifespan=db_lifespan)

app.include_router(router)

# CORS - use the validated allowed_origins property and convert to strings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(u) for u in settings.allowed_origins],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "civ-save-tool", "status": "ok"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz(db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        await db.command("ping")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(503, f"DB not ready: {e!s}")

@app.get("/_debug/db-stats")
async def db_stats(db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        stats = await db.command("dbstats", scale=1)
        return JSONResponse(stats)
    except Exception as e:
        raise HTTPException(503, f"DB not ready: {e!s}")