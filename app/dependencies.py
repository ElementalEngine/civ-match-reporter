from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase

def get_database(request: Request) -> AsyncIOMotorDatabase:
    db = getattr(request.app.state, "mongodb", None)
    if db is None:
        raise RuntimeError("Mongo database not initialized")
    return db