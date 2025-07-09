from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class DashboardProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_name = Column(String(100), nullable=False)
    bet_amount = Column(Integer, nullable=False)
    selected_patterns = Column(JSON, nullable=False)
    selected_game_ids = Column(JSON, nullable=False)
    api_source = Column(String(20), nullable=False, default='old')
    dashboard_type = Column(String(50), nullable=False, default='nhl_dashboard')
    game_pattern_bets = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="dashboard_profiles")
    
    # Unique constraint - include api_source and dashboard_type
    __table_args__ = (UniqueConstraint('user_id', 'profile_name', 'api_source', 'dashboard_type', name='unique_user_profile_source_type'),)