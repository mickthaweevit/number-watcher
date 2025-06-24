from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    base_game_id = Column(String(50), unique=True, index=True, nullable=False)  # "L03-01-000500"
    game_name = Column(String(200), nullable=False)  # "ดาวโจนส์ VIP"
    country_code = Column(String(10), nullable=True)  # "US", "LA", "VN"
    category = Column(String(50), nullable=False)  # "settrade", "settradeInt", "set"
    is_active = Column(Boolean, default=True)  # for hiding/showing games
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to Results
    results = relationship("Result", back_populates="game")