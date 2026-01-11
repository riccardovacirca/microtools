from fastapi import APIRouter, HTTPException
from .services import info_service
from .models import info_models

router = APIRouter()

@router.get("/info", response_model=info_models.InfoResponse)
async def app_info():
    """Endpoint per ottenere lo stato dell'applicazione.

    Restituisce i dati della tabella app_status:
    - Prima controlla la cache Redis
    - Se non presente, invoca il microservizio C++ che legge dal database
    """
    output = {}
    success = await info_service.get_info(output=output)
    if success:
        return info_models.InfoResponse(**output)
    else:
        raise HTTPException(
            status_code=503,
            detail=output.get("error", "Failed to retrieve app_status")
        )
