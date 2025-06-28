from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from .game import Game

class ResultBase(BaseModel):
    game_id: int
    full_game_code: str
    result_date: date
    result_3up: Optional[str] = None
    result_2down: Optional[str] = None
    result_4up: Optional[str] = None
    status: str = "completed"

class ResultCreate(ResultBase):
    pass

class Result(ResultBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    game: Game

    class Config:
        from_attributes = True

# Alias for backward compatibility
ResultResponse = Result