from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GameBase(BaseModel):
    base_game_id: str
    game_name: str
    is_active: bool = True

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alias for backward compatibility
GameResponse = Game