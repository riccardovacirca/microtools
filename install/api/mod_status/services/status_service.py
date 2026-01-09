import time
import json
import redis
import os
from ..adapters import cpp_adapter
from ..models import response_models

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

async def get_health() -> response_models.HealthResponse:
    """Verifica lo stato di salute del servizio C++ mod_status.

    Logica di dominio: orchestrazione del controllo di salute,
    può aggiungere validazioni o logiche di retry se necessario.
    """
    try:
        info = await cpp_adapter.get_runtime_info()
        return response_models.HealthResponse(
            status="healthy",
            service="mod_status",
            timestamp=int(time.time())
        )
    except Exception:
        return response_models.HealthResponse(
            status="unhealthy",
            service="mod_status",
            timestamp=int(time.time())
        )

async def get_version() -> response_models.VersionResponse:
    """Ottiene la versione del servizio C++ mod_status.

    Logica di dominio: estrazione e formattazione delle informazioni di versione.
    """
    info = await cpp_adapter.get_runtime_info()
    return response_models.VersionResponse(
        version=info.get("version", "unknown"),
        name=info.get("name", "mod_status"),
        environment=info.get("environment", "development")
    )

async def get_info() -> response_models.InfoResponse:
    """Ottiene le informazioni dell'applicazione da Redis o dal microservizio C++.

    Logica:
    1. Controlla se esiste la chiave "app_status" in Redis
    2. Se esiste, restituisce il valore cached
    3. Se non esiste, invoca il microservizio C++ che:
       - Legge dal database
       - Salva in Redis
       - Restituisce i dati

    Returns:
        InfoResponse: Informazioni dell'applicazione (id, version, timestamps)

    Raises:
        Exception: Se Redis fallisce o il microservizio C++ non è raggiungibile
    """
    try:
        # Step 1: Check Redis cache
        cached_data = redis_client.get("app_status")

        if cached_data:
            # Cache hit: deserialize and return
            data = json.loads(cached_data)
            return response_models.InfoResponse(**data)

        # Step 2: Cache miss - invoke C++ microservice
        # The C++ service will read from DB and populate Redis
        info = await cpp_adapter.get_runtime_info()

        # Return the data received from C++ microservice
        return response_models.InfoResponse(**info)

    except redis.RedisError as e:
        # If Redis fails, fallback to C++ microservice
        info = await cpp_adapter.get_runtime_info()
        return response_models.InfoResponse(**info)
