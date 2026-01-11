import json
import redis
import os
from typing import Dict, Any
from pydantic import ValidationError
from ..adapters import info_adapter
from ..models import info_models

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

async def get_info(output: Dict[str, Any]) -> bool:
    """Ottiene le informazioni dell'applicazione da Redis o dal microservizio C++.

    Logica:
    1. Controlla se esiste la chiave "app_status" in Redis
    2. Se esiste, restituisce il valore cached
    3. Se non esiste, invoca il microservizio C++ che:
       - Legge dal database
       - Salva in Redis
       - Restituisce i dati

    Args:
        output: Dizionario per memorizzare il risultato validato

    Returns:
        bool: True se l'operazione ha successo, False altrimenti
    """
    class Err:
        redis_access: bool = False
        adapter_call: bool = False
        validation: bool = False

    retv: bool = False
    result: Dict[str, Any] = {}
    error: str | None = None

    try:
        cached_data = redis_client.get("app_status")

        if cached_data:
            data = json.loads(cached_data)
            info_response = info_models.InfoResponse(**data)
            result.update(info_response.model_dump())
            retv = True
        else:
            info = await info_adapter.get_runtime_info()
            info_response = info_models.InfoResponse(**info)
            result.update(info_response.model_dump())
            retv = True

    except redis.RedisError as e:
        try:
            Err.redis_access = True
            info = await info_adapter.get_runtime_info()
            info_response = info_models.InfoResponse(**info)
            result.update(info_response.model_dump())
            retv = True
        except Exception as fallback_error:
            Err.adapter_call = True
            raise ValueError()

    except Exception as e:
        if Err.redis_access:
            error = "Redis access failed and C++ adapter fallback failed"
        elif Err.adapter_call:
            error = "Failed to call C++ adapter"
        elif Err.validation:
            error = "Info data validation failed"
        else:
            error = str(e) or "Unknown error"

    if retv:
        output.update(result)
    else:
        output["error"] = error

    return retv
