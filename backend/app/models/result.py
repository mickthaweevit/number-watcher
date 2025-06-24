from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    full_game_code = Column(String(100), nullable=False)  # "L03-01-000500-20250622"
    result_date = Column(Date, nullable=False)  # "2025-06-22"
    result_3up = Column(String(10), nullable=True)  # 3-digit result
    result_2down = Column(String(10), nullable=True)  # 2-digit result
    result_4up = Column(String(10), nullable=True)  # 4-digit result
    status = Column(String(20), default="completed")  # 'waiting', 'cancelled', 'completed', 'no_result'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to Game
    game = relationship("Game", back_populates="results")

    # Unique constraint to prevent duplicate results for same game+date
    __table_args__ = (UniqueConstraint('game_id', 'result_date', name='unique_game_date'),)