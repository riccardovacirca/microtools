from pydantic import BaseModel
from typing import Dict, Any

class ResponseModel(BaseModel):
    """Response standard per tutti i service: {err, log, out}."""
    err: bool
    log: str | None
    out: Any | None

def get(err: bool, log: str | None, out: Any | None) -> Dict[str, Any]:
    """Serializza ResponseModel in dict."""
    retv = ResponseModel(err=err, log=log, out=out)
    return retv.model_dump()
