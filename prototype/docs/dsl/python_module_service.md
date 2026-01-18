SERVICE_STYLE explicit_async_service

INTERFACE:
  - async functions only
  - no framework-specific types in signature
  - return type: Dict[str, Any]

ARCHITECTURE:
  - services contain business logic and orchestration
  - adapters handle external HTTP services only
  - Redis cache managed directly in service (no adapter)
  - models handle validation and normalization
  - services orchestrate: adapters + cache + models

DATA_FLOW:
  - raw data from adapter or Redis cache
  - validation via Pydantic models
  - output via response_model.get()

RESPONSE_MODEL:
  - MANDATORY: all services must return response_model.get()
  - fields: err (bool), log (str|None), out (Any|None)
  - all parameters required (no defaults)
  - success: response_model.get(False, None, validated_data)
  - error: response_model.get(True, "error message", None)

ERROR_HANDLING:
  - no exceptions leaked outside service
  - all errors caught and mapped to response_model
  - always return dict, never raise

FUNCTION_PARAMETERS:
  - NO default values allowed in function signatures
  - All parameters must be explicit
  - Rationale: explicit over implicit, no arbitrary usage
  - Example forbidden: def func(a, b=None)
  - Example required: def func(a, b)

FORBIDDEN:
  - raising HTTPException
  - returning Response objects
  - accessing framework Request/Response
  - returning raw adapter data without validation
