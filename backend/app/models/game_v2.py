from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class GameV2(Base):
    __tablename__ = "games_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    product_name_th = Column(String(255))
    product_code = Column(String(10), index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    results = relationship("ResultV2", back_populates="game")