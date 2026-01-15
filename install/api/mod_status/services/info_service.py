import json
import redis
import os
from typing import Dict, Any
from pydantic import ValidationError
from ..adapters import info_adapter
from ..models import info_model
from ..models import response_model

# Client Redis per cache
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

async def get() -> Dict[str, Any]:
    """Recupera info status da cache o microservizio."""
    try:
        # Prova cache Redis
        rval = redis_client.get("app_status")
        if rval:
            data = json.loads(rval)
        else:
            data = await info_adapter.get()

        # Valida e restituisci
        retv = info_model.get(data)
        return response_model.get(False, None, retv.model_dump())

    except redis.RedisError:
        # Fallback a microservizio se Redis fallisce
        try:
            data = await info_adapter.get()
            retv = info_model.get(data)
            return response_model.get(False, None, retv.model_dump())
        except Exception:
            return response_model.get(True, "Redis access failed", None)

    except ValidationError:
        return response_model.get(True, "Info data validation failed", None)

    except Exception as e:
        return response_model.get(True, str(e) or "Unknown error", None)
