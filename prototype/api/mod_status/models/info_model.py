
from pydantic import BaseModel, Field

class InfoModel(BaseModel):
    """Dati status applicazione."""
    id: int = Field(..., ge=1)
    version: str = Field(..., min_length=1)
    created_at: str = Field(..., min_length=1)
    updated_at: str = Field(..., min_length=1)

    class Config:
        extra = "allow"

def get(data: dict) -> InfoModel:
    """Valida e restituisce InfoModel."""
    return InfoModel(**data)
