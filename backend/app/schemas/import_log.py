from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ImportLogBase(BaseModel):
    filename: Optional[str] = None
    import_type: str
    records_processed: int = 0
    games_created: int = 0
    results_created: int = 0
    error_message: Optional[str] = None
    file_size: Optional[int] = None

class ImportLogCreate(ImportLogBase):
    pass

class ImportLog(ImportLogBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True

# Alias for backward compatibility
ImportLogResponse = ImportLog