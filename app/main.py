from fastapi import FastAPI
from app.routes import parse, finalize, reparse, flag, approve

app = FastAPI()

app.include_router(parse.router, prefix="/parse")
app.include_router(finalize.router, prefix="/finalize")
app.include_router(reparse.router, prefix="/reparse")
app.include_router(flag.router, prefix="/flag")
app.include_router(approve.router, prefix="/approve")

@app.get("/")
def root():
    return {"status": "ok"}


# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

CIV_SAVE_PARSER_VERSION = os.getenv("CIV_SAVE_PARSER_VERSION", "dev")