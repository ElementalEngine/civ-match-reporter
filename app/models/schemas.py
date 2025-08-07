from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlayerSchema(BaseModel):
    steam_id: str
    user_name: str
    civ: str
    team: int
    leader: Optional[str] = None
    player_alive: Optional[bool] = None
    discord_id: Optional[str] = None
    placement: Optional[int] = None

class MatchResponse(BaseModel):
    match_id: str
    game: str
    turn: int
    age: Optional[int] = None
    map_type: str
    game_mode: str
    players: List[PlayerSchema]
    parser_version: str
    created_at: datetime
    confirmed: bool
    flagged: bool
    flagged_by: Optional[str] = None

class MatchUpdate(BaseModel):
    players: Optional[List[PlayerSchema]] = None
    confirmed: Optional[bool] = None
    flagged: Optional[bool] = None
    flagged_by: Optional[str] = None