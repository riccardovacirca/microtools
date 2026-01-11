from pydantic import BaseModel, Field

class InfoResponse(BaseModel):
    """Application status information from database.

    Contains application version and metadata from app_status table.
    """
    id: int = Field(..., ge=1)
    version: str = Field(..., min_length=1)
    created_at: str = Field(..., min_length=1)
    updated_at: str = Field(..., min_length=1)

    class Config:
        extra = "allow"
