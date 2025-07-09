from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional, Any

class DashboardProfileCreate(BaseModel):
    profile_name: str
    bet_amount: Optional[int] = 0
    selected_patterns: Optional[List[str]] = []
    selected_game_ids: Optional[List[int]] = []
    api_source: str = 'old'
    dashboard_type: str = 'nhl_dashboard'
    game_pattern_bets: Optional[Dict[str, Any]] = None
    
    # Allow extra fields for different dashboard types
    class Config:
        extra = "allow"

class DashboardProfileUpdate(BaseModel):
    profile_name: str
    bet_amount: Optional[int] = 0
    selected_patterns: Optional[List[str]] = []
    selected_game_ids: Optional[List[int]] = []
    api_source: str = 'old'
    dashboard_type: str = 'nhl_dashboard'
    game_pattern_bets: Optional[Dict[str, Any]] = None
    
    # Allow extra fields for different dashboard types
    class Config:
        extra = "allow"

class DashboardProfileResponse(BaseModel):
    id: int
    user_id: int
    profile_name: str
    bet_amount: int
    selected_patterns: List[str]
    selected_game_ids: List[int]
    api_source: str
    dashboard_type: str
    game_pattern_bets: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True