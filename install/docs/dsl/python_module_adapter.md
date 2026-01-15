ADAPTER_STYLE explicit_async_adapter

INTERFACE:
  - async functions only
  - return type: Dict[str, Any]
  - no framework-specific types

RESPONSIBILITY:
  - adapters perform I/O only
  - no business logic
  - no validation
  - no response shaping

DATA:
  - return raw external data
  - no normalization
  - no default values

ERRORS:
  - propagate transport errors
  - no error wrapping
  - no logging policy enforced

CONFIG:
  - configuration via environment variables only
  - no hardcoded endpoints

FUNCTION_PARAMETERS:
  - NO default values allowed in function signatures
  - All parameters must be explicit
  - Rationale: explicit over implicit

FORBIDDEN:
  - pydantic models
  - response_model usage
  - service imports
  - retry logic
