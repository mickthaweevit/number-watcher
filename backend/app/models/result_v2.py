from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class ResultV2(Base):
    __tablename__ = "results_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games_v2.id"), index=True)
    period_id = Column(Integer)
    award1 = Column(String(20))
    award2 = Column(String(20))
    award3 = Column(String(100))
    result_date = Column(Date, index=True)
    status = Column(String(20), default="completed")
    yk_round = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    game = relationship("GameV2", back_populates="results")