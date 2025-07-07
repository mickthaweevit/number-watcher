from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

class DashboardProfileCreate(BaseModel):
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]
    api_source: str = 'old'
    game_pattern_bets: Optional[Dict[int, Dict[str, int]]] = None

class DashboardProfileUpdate(BaseModel):
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]
    api_source: str = 'old'
    game_pattern_bets: Optional[Dict[int, Dict[str, int]]] = None

class DashboardProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]
    api_source: str
    game_pattern_bets: Optional[Dict[int, Dict[str, int]]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True