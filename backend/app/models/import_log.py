from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from ..database import Base

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)  # "backup-2025-06-27.json"
    import_type = Column(String(50), nullable=False)  # "backup", "date_range", "sample_data"
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)  # NULL if running
    status = Column(String(20), default="running")  # "running", "success", "failed"
    records_processed = Column(Integer, default=0)  # Number of records processed
    games_created = Column(Integer, default=0)  # Games created
    results_created = Column(Integer, default=0)  # Results created
    error_message = Column(Text, nullable=True)  # Error details if failed
    file_size = Column(BigInteger, nullable=True)  # File size in bytes