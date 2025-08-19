from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PlayerModel(BaseModel):
    steam_id: Optional[str] = None
    user_name: Optional[str] = None
    civ: str
    team: int
    leader: Optional[str] = None
    player_alive: Optional[bool] = None
    discord_id: Optional[str] = None
    placement: Optional[int] = None

class MatchModel(BaseModel):
    game: str  # parsers return "civ6" or "civ7"
    turn: int
    age: Optional[int] = None
    map_type: str
    game_mode: str  # allow "", "ffa", "team", "duel"
    players: List[PlayerModel]
    parser_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed: bool = False
    flagged: bool = False
    flagged_by: Optional[str] = None
    save_file_hash: str