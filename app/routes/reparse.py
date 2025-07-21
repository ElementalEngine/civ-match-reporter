from fastapi import APIRouter, Body
from app.config import MATCH_STORAGE
from app.parsers.civ6 import parse_civ6_save
from app.parsers.civ7 import parse_civ7_save

router = APIRouter()

@router.post("/")
def reparse(match_id: str = Body(...), file: UploadFile = File(...)):
    content = file.file.read()
    if match_id not in MATCH_STORAGE:
        return {"error": "Match ID not found"}

    if file.filename.endswith(".Civ6Save"):
        updated = parse_civ6_save(content)
    elif file.filename.endswith(".Civ7Save"):
        updated = parse_civ7_save(content)
    else:
        return {"error": "Unsupported file"}

    updated["match_id"] = match_id
    MATCH_STORAGE[match_id] = updated
    return updated
