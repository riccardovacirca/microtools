SERVICE_STYLE explicit_async_service

INTERFACE:
  - async functions only
  - no framework-specific types in signature
  - return type: Dict[str, Any]

ARCHITECTURE:
  - services contain business logic and orchestration
  - adapters handle external HTTP services
  - cache access via private helper functions
  - models handle validation
  - response_model for output normalization

STRUCTURE:

  Helper functions:
  - private (prefixed with _)
  - isolate cache access and reusable logic
  - naming: _<action>_<resource> or _<action>
  - sync allowed
  - return type: Dict[str, Any] | None
  - example: _get_cached() -> Dict[str, Any] | None

  Main function:
  - signature: async def <action>() -> Dict[str, Any]
  - variables initialized at start:
      err = False
      log: str | None = None
      out: Dict[str, Any] | None = None
  - single try block with main logic
  - except blocks for specific exceptions
  - single return statement

CONTROL_FLOW:
  - single try block (no nesting)
  - single exit point
  - return pattern: response_model.set(err, log, out)

ERROR_HANDLING:
  - no exceptions leaked outside service
  - catch and map to err/log variables
  - except blocks ordered specific to generic
  - pattern:
      except SpecificError as e:
          err = True
          log = str(e) or "Error message"

RESPONSE_MODEL:
  - MANDATORY for all services
  - fields: err (bool), log (str|None), out (Dict|None)
  - success: response_model.set(False, None, validated_data)
  - error: response_model.set(True, "message", None)

DATA_FLOW:
  1. helper function or adapter for raw data
  2. model.get(data) for INPUT validation
  3. response_model.set(err, log, out) for OUTPUT

FUNCTION_PARAMETERS:
  - NO default values allowed
  - all parameters explicit
  - forbidden: def func(a, b=None)
  - required: def func(a, b)

FORBIDDEN:
  - HTTPException, Response, Request
  - raw adapter output without validation
  - nested try/except blocks
  - multiple return statements
  - business logic in except blocks
  - default parameter values

EXAMPLE:

```python
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
```
