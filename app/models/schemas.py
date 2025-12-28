from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlayerSchema(BaseModel):
    steam_id: Optional[str] = None
    user_name: Optional[str] = None
    civ: str
    team: int
    leader: Optional[str] = None
    player_alive: Optional[bool] = None
    discord_id: Optional[str] = None
    placement: Optional[int] = None
    quit: bool
    delta: float = 0.0
    sub_of: Optional[str] = None

class MatchResponse(BaseModel):
    match_id: str
    game: str
    turn: int
    age: Optional[int] = None
    map_type: str
    game_mode: str
    players: List[PlayerSchema]
    parser_version: str
    discord_messages_id_list: List[str]
    created_at: datetime
    approved_at: Optional[datetime] = None
    approver_discord_id: Optional[str] = None
    flagged: bool
    flagged_by: Optional[str] = None
    reporter_discord_id: str

class MatchUpdate(BaseModel):
    match_id: str
    players: Optional[List[PlayerSchema]] = None
    confirmed: Optional[bool] = None
    flagged: Optional[bool] = None
    flagged_by: Optional[str] = None

class ChangeOrder(BaseModel):
    match_id: str
    new_order: str # The order of players as a string, e.g. "1 2 3 4" separated by spaces

class DeletePendingMatch(BaseModel):
    match_id: str

class TriggerQuit(BaseModel):
    match_id: str
    quitter_discord_id: str
    discord_message_id: str

class AppendDiscordMessageID(BaseModel):
    match_id: str
    discord_message_id: List[str]

class AssignDiscordId(BaseModel):
    match_id: str
    player_id: str
    player_discord_id: str
    discord_message_id: str

class ApproveMatch(BaseModel):
    match_id: str
    approver_discord_id: str