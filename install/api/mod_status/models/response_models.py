from pydantic import BaseModel, Field
from typing import Any, Dict

class HealthResponse(BaseModel):
    """Health check response with service status and timestamp.

    Used by status endpoints to report service availability.
    """
    status: str = Field(..., min_length=1, max_length=20)
    service: str = Field(..., min_length=1, max_length=50)
    timestamp: int = Field(..., ge=0)

class VersionResponse(BaseModel):
    """Service version information.

    Provides version, service name, and environment details.
    """
    version: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    environment: str = Field(..., min_length=1, max_length=20)

class InfoResponse(BaseModel):
    """Application status information from database.

    Contains application version and metadata from app_status table.
    """
    id: int
    version: str
    created_at: str
    updated_at: str

    class Config:
        extra = "allow"  # Allow additional fields from JSON
