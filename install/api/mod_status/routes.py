from fastapi import APIRouter, HTTPException
from .services import status_service
from .models import response_models

router = APIRouter()

@router.get("/health", response_model=response_models.HealthResponse)
async def health_check():
    """Endpoint per verificare lo stato di salute del servizio."""
    return await status_service.get_health()

@router.get("/version", response_model=response_models.VersionResponse)
async def version_info():
    """Endpoint per ottenere informazioni sulla versione del servizio."""
    try:
        return await status_service.get_version()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"mod_status service unavailable: {str(e)}"
        )

@router.get("/info", response_model=response_models.InfoResponse)
async def app_info():
    """Endpoint per ottenere lo stato dell'applicazione.

    Restituisce i dati della tabella app_status:
    - Prima controlla la cache Redis
    - Se non presente, invoca il microservizio C++ che legge dal database
    """
    try:
        return await status_service.get_info()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to retrieve app_status: {str(e)}"
        )
