import logging
from typing import Optional
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

def init_db(app: FastAPI) -> None:
    @app.on_event("startup")
    async def _connect_db():
        try:
            app.state.mongodb_client = AsyncIOMotorClient(
                settings.mongodb_uri.get_secret_value(),
                serverSelectionTimeoutMS=settings.mongodb_timeout_ms,
                maxPoolSize=settings.mongodb_max_pool_size,
                minPoolSize=settings.mongodb_min_pool_size,
            )
            await app.state.mongodb_client.server_info()
            app.state.mongodb = app.state.mongodb_client[settings.mongodb_db_name]
            logger.info("🟢 MongoDB connected")
        except Exception:
            logger.exception("🔴 Failed to connect to MongoDB")
            raise

    @app.on_event("shutdown")
    async def _close_db():
        client: Optional[AsyncIOMotorClient] = getattr(app.state, "mongodb_client", None)
        if client:
            client.close()
            logger.info("🟠 MongoDB connection closed")