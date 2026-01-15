API_STYLE fastapi_explicit_starlette_servlet

ROUTING:
  - use APIRouter
  - decorators only
  - no global app routes

HANDLERS:
  - async only
  - Request imported ONLY if used
  - when Request needed: servlet-like style
    example: data = await request.json()
  - no Depends
  - no Pydantic models in signature

ARCHITECTURE:
  - handlers delegate to services
  - services return response_model dict
  - handlers are thin HTTP layer

REQUEST_BODY_PARSING:
  - for POST/PUT: use Request parameter
  - parse with: data = await request.json()
  - validate with: body = InputModel(**data)
  - servlet-like explicit parsing

RESPONSES:
  - JSONResponse only
  - explicit status code required
  - positional parameters allowed: JSONResponse(data, 200)
  - always return complete response_model structure

ERROR_HANDLING:
  - check data["err"] flag
  - if err=True: status 503
  - if err=False: status 200
  - return complete dict {err, log, out}

FUNCTION_PARAMETERS:
  - NO default values allowed in function signatures
  - All parameters must be explicit
  - Rationale: explicit over implicit

FORBIDDEN:
  - response_model decorator
  - implicit body parsing via Pydantic signature
  - implicit status codes
  - HTTPException
  - unused imports
