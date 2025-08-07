import os
from dotenv import load_dotenv
from pathlib import Path

# Load from .env (project root)
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

def require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is not set.")
    return value

# Required: no defaults for secrets
CIV_SAVE_PARSER_VERSION = os.getenv("CIV_SAVE_PARSER_VERSION", "dev")

# Required: fail fast if not set
MONGO_URI = require_env("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "match_reporter")

# Optional: use defaults for local dev
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Safe default: only allow local by default
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")