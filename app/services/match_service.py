import logging
from typing import Any, Dict
from bson import ObjectId
from app.parsers import parse_civ7_save, parse_civ6_save  # do not modify parser code
from app.config import settings
from app.models.db_models import MatchModel

logger = logging.getLogger(__name__)

class MatchServiceError(Exception): ...
class InvalidIDError(MatchServiceError): ...
class ParseError(MatchServiceError): ...
class NotFoundError(MatchServiceError): ...

class MatchService:
    def __init__(self, db):
        self.db = db
        self.col = db.pending_matches

    @staticmethod
    def _to_oid(match_id: str) -> ObjectId:
        try:
            return ObjectId(match_id)
        except Exception:
            raise InvalidIDError("Invalid match ID")

    @staticmethod
    def _parse_save(file_bytes: bytes) -> Dict[str, Any]:
        for parser in (parse_civ7_save, parse_civ6_save):
            try:
                data = parser(file_bytes, settings.civ_save_parser_version)
                logger.info(f"✅ 🔍 Parsed as {data.get('game')}")
                return data
            except Exception as e:
                logger.warning(f"⚠️ Parse attempt failed: {e}")
        raise ParseError("Unrecognized save file format")

    async def create_from_save(self, file_bytes: bytes) -> Dict[str, Any]:
        parsed = self._parse_save(file_bytes)
        match = MatchModel(**parsed)
        res = await self.col.insert_one(match.dict())
        return {"match_id": str(res.inserted_id), **match.dict()}

    async def get(self, match_id: str) -> Dict[str, Any]:
        oid = self._to_oid(match_id)
        doc = await self.col.find_one({"_id": oid})
        if not doc:
            raise NotFoundError("Match not found")
        doc["match_id"] = str(doc.pop("_id"))
        return doc

    async def update(self, match_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        if not update_data:
            raise MatchServiceError("Empty update payload")
        oid = self._to_oid(match_id)
        res = await self.col.update_one({"_id": oid}, {"$set": update_data})
        if res.matched_count == 0:
            raise NotFoundError("Match not found")
        updated = await self.col.find_one({"_id": oid})
        updated["match_id"] = str(updated.pop("_id"))
        logger.info(f"✅ 🔄 Updated match {match_id}")
        return updated