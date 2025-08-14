import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routes.upload import router as upload_router
from app.routes.matches import router as matches_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Civ Match Reporter API",
    version=settings.civ_save_parser_version
)

# CORS (adjust ALLOWED_ORIGINS in .env if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB lifecycle
init_db(app)

# Routers
app.include_router(upload_router)
app.include_router(matches_router)

@app.get("/", tags=["health"])
async def root():
    return {"status": "🟢 OK"}
