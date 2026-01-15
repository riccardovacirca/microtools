from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .services import info_service

router = APIRouter()

@router.get("/info")
async def info_handler():
    """Endpoint info status applicazione."""
    data = await info_service.get()

    if data["err"]:
        return JSONResponse(data, 503)
    return JSONResponse(data, 200)
