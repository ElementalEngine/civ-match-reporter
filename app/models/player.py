from pydantic import BaseModel

class Player(BaseModel):
    steam_id: str
    civ: str
    team: int