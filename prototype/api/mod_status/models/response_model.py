from pydantic import BaseModel
from typing import Any, Optional

class ResponseModel(BaseModel):
    """Response standard per tutti i service: {err, log, out}."""
    err: bool
    log: Optional[str]
    out: Optional[Any]

def get(err: bool, log: Optional[str], out: Optional[Any]) -> dict:
    """Serializza ResponseModel in dict."""
    model = ResponseModel(err=err, log=log, out=out)
    return model.model_dump()
