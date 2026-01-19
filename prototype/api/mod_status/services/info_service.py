import json
import redis
import os
from typing import Dict, Any
from pydantic import ValidationError
from ..adapters import info_adapter
from ..models import info_model
from ..models import response_model

def _get_cached() -> Dict[str, Any] | None:
    """Recupera dati da cache Redis, None se fallisce."""
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "127.0.0.1"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True
    )
    rval = redis_client.get("app_status")
    if rval:
        return json.loads(rval)
    return None

async def get() -> Dict[str, Any]:
    """Recupera info status da cache o microservizio."""
    err = False
    log: str | None = None
    out: Dict[str, Any] | None = None
    try:
        rval: Dict[str, Any] | None = _get_cached()
        if rval is None:
            rval = await info_adapter.get()
        out = info_model.get(rval)
    except redis.RedisError as e:
        err = True
        log = str(e) or "Redis error"
    except json.JSONDecodeError as e:
        err = True
        log = str(e) or "JSON decode error"
    except ValidationError:
        err = True
        log = "Info data validation failed"
    except Exception as e:
        err = True
        log = str(e) or "Unknown error"
    return response_model.set(err, log, out)
