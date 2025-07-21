from pydantic import BaseModel
from typing import List
from .player import Player

class Match(BaseModel):
    match_id: str
    game: str
    turn: int
    cloud_game: bool
    players: List[Player]
    game_mode: str
    parser_version: str
