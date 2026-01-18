API_STYLE fastapi_explicit_starlette_servlet

# ROUTER DECLARATION

MANDATORY PREFIX:
  - Every module router MUST have a prefix
  - Prefix = module name WITHOUT "mod_" prefix
  - Pattern: mod_<name> -> prefix="/<name>"

  Examples:
    mod_status  -> router = APIRouter(prefix="/status", tags=["status"])
    mod_risorse -> router = APIRouter(prefix="/risorse", tags=["risorse"])
    mod_auth    -> router = APIRouter(prefix="/auth", tags=["auth"])

DECLARATION:
```python
router = APIRouter(prefix="/<module>", tags=["<module>"])
```

# ROUTING

PATH CONVENTION:
  - Paths are RELATIVE to router prefix
  - Pattern: /<entity_name>
  - Full URL: /api/<module>/<entity> (when mounted on /api)

  Examples:
    @router.get("/info")           -> /status/info
    @router.get("/contatti")       -> /risorse/contatti
    @router.get("/contatti/{id}")  -> /risorse/contatti/{id}

CRUD PATHS:
  - LIST:   GET    /<entity>
  - CREATE: POST   /<entity>
  - READ:   GET    /<entity>/{id}
  - UPDATE: PUT    /<entity>/{id}
  - DELETE: DELETE /<entity>/{id}
  - NESTED: GET    /<entity>/{id}/<sub_entity>

# HANDLERS

NAMING:
  - camelCase: getContatti, getContattoById, createContatto

ASYNC:
  - ALL handlers must be async

REQUEST USAGE:
  - Import Request ONLY if used
  - For body: data = await request.json()
  - For pool: pool = request.app.state.db_pool
  - Servlet-style explicit parsing

NO DEPENDS:
  - Do not use Depends()
  - Do not use Pydantic in signature

# ARCHITECTURE

HANDLER RESPONSIBILITY:
  - Thin HTTP layer only
  - Delegate to services
  - Check err flag for status code

SERVICE RETURN:
  - Services return response_model dict
  - Handler returns JSONResponse with dict

# RESPONSES

TYPE:
  - JSONResponse only
  - Explicit status code required

ERROR HANDLING:
  - Check data["err"] flag
  - if err=True: status 503
  - if err=False: status 200

STRUCTURE:
  - Always return complete {err, log, out}

# FUNCTION PARAMETERS

RULE:
  - NO default values
  - All parameters explicit

FORBIDDEN:
  ✗ async def handler(request: Request = None)

REQUIRED:
  ✓ async def handler(request: Request)

# FORBIDDEN PATTERNS

- response_model decorator
- implicit body parsing via Pydantic signature
- implicit status codes
- HTTPException
- unused imports
- default parameter values
- router without prefix

# COMPLETE EXAMPLE

```python
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .services import contatto_service

router = APIRouter(prefix="/risorse", tags=["risorse"])

@router.get("/contatti")
async def getContatti(request: Request):
    """Recupera tutti i contatti."""
    pool = request.app.state.db_pool
    data = await contatto_service.getAll(pool)
    if data["err"]:
        return JSONResponse(data, 503)
    return JSONResponse(data, 200)

@router.get("/contatti/{id}")
async def getContattoById(request: Request, id: int):
    """Recupera contatto per id."""
    pool = request.app.state.db_pool
    data = await contatto_service.getById(pool, id)
    if data["err"]:
        return JSONResponse(data, 503)
    return JSONResponse(data, 200)

@router.post("/contatti")
async def createContatto(request: Request):
    """Crea nuovo contatto."""
    pool = request.app.state.db_pool
    body = await request.json()
    data = await contatto_service.create(pool, body)
    if data["err"]:
        return JSONResponse(data, 503)
    return JSONResponse(data, 200)
```
