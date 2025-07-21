import os
from dotenv import load_dotenv

load_dotenv()

CIV_SAVE_PARSER_VERSION = os.getenv("CIV_SAVE_PARSER_VERSION", "dev")

# In-memory store for demo/testing
MATCH_STORAGE = {}
CONFIRMED_PLACEMENTS = {}
MATCH_FLAGS = {}
RATINGS = {}