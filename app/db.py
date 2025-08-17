import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

# Ensure startup logs are visible when running directly (won't override existing handlers)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

logger = logging.getLogger("app.db")

@asynccontextmanager
async def db_lifespan(app: FastAPI):
    uri = settings.mongo_url.get_secret_value()
    if not uri:
        raise RuntimeError("MONGO_URL is required")

    timeout_ms = settings.mongodb_timeout_ms
    min_pool = settings.mongodb_min_pool_size
    max_pool = settings.mongodb_max_pool_size

    client: Optional[AsyncIOMotorClient] = None
    try:
        client = AsyncIOMotorClient(
            uri,
            uuidRepresentation="standard",
            minPoolSize=min_pool,
            maxPoolSize=max_pool,
            connectTimeoutMS=timeout_ms,
            serverSelectionTimeoutMS=timeout_ms,
            socketTimeoutMS=timeout_ms,
            retryReads=True,
            retryWrites=True,
        )

        # ensure we can talk to the server
        await client.admin.command("ping")

        db: Optional[AsyncIOMotorDatabase] = client[settings.mongo_db_name]
        app.state.mongodb_client = client
        app.state.mongodb = db
        logger.info("🟢 MongoDB connected (db=%s)", db.name)

        yield  # application runs while yielded

    except Exception:
        logger.exception("🔴 Failed to connect to MongoDB")
        # Ensure client closed on error
        if client:
            client.close()
        raise
    finally:
        client = getattr(app.state, "mongodb_client", None)
        if client:
            client.close()
            logger.info("🟠 MongoDB connection closed")