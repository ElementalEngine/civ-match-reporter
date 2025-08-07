from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class PlayerModel(BaseModel):
    steam_id: str
    user_name: str
    civ: str
    team: int
    # Civ7 parser adds leader
    leader: Optional[str] = None
    player_alive: Optional[bool] = None
    # Will be populated when user links Discord
    discord_id: Optional[str] = None
    # User-provided placement before confirmation
    placement: Optional[int] = None


class MatchModel(BaseModel):
    game: Literal["Civ6", "Civ7"]
    turn: int
    # Civ7 includes game age
    age: Optional[int] = None
    map_type: str
    game_mode: Literal["ffa", "team", "duel"]
    players: List[PlayerModel]
    parser_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed: bool = Field(default=False)
    flagged: bool = Field(default=False)
    flagged_by: Optional[str] = None