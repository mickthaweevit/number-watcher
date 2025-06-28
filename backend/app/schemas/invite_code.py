from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InviteCodeCreate(BaseModel):
    expires_at: Optional[datetime] = None

class InviteCodeResponse(BaseModel):
    id: int
    code: str
    created_by: int
    used_by: Optional[int] = None
    is_used: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserRegisterWithInvite(BaseModel):
    username: str
    email: str
    password: str
    invite_code: str