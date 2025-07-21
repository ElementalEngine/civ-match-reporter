from fastapi import APIRouter, UploadFile, File
from app.parsers.civ6 import parse_civ6_save
from app.parsers.civ7 import parse_civ7_save

router = APIRouter()

@router.post("/")
def parse(file: UploadFile = File(...)):
    content = file.file.read()
    if file.filename.endswith(".Civ6Save"):
        return parse_civ6_save(content)
    elif file.filename.endswith(".Civ7Save"):
        return parse_civ7_save(content)
    return {"error": "Unsupported file"}
