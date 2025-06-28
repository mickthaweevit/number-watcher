from pydantic import BaseModel
from datetime import datetime
from typing import List

class DashboardProfileCreate(BaseModel):
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]

class DashboardProfileUpdate(BaseModel):
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]

class DashboardProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True