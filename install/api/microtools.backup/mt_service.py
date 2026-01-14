"""Service layer pattern utilities.

This module standardizes the service pattern used throughout the application:
- Execute business logic in try/except block
- Populate output dictionary with results or error
- Return boolean success status

Functions follow naming convention: mt_service_<functionality>()
"""

from typing import Dict, Any, Callable, TypeVar

T = TypeVar('T')


def mt_service_execute(
    operation: Callable[[], T],
    output: Dict[str, Any],
    transform: Callable[[T], Dict[str, Any]] | None = None
) -> bool:
    """Execute service operation with standardized error handling and output population.

    Eliminates the repeated pattern:
        retv: bool = False
        result: Dict[str, Any] = {}
        error: str | None = None
        try:
            data = operation()
            result.update(transform(data))
            retv = True
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
        if retv:
            output.update(result)
        else:
            output["error"] = error
        return retv

    Args:
        operation: Function to execute (should raise exceptions on error)
        output: Dictionary to populate with results or error
        transform: Optional function to transform result to dict (if None, result must be dict)

    Returns:
        True if successful, False otherwise (error in output['error'])

    Example:
        # Simple case - operation returns dict
        >>> output = {}
        >>> success = mt_service_execute(
        ...     lambda: {"id": 1, "name": "John"},
        ...     output
        ... )
        >>> print(output)  # {"id": 1, "name": "John"}

        # With transform - operation returns object
        >>> output = {}
        >>> success = mt_service_execute(
        ...     lambda: get_user_by_id(1),
        ...     output,
        ...     transform=lambda user: user.model_dump()
        ... )
    """
    try:
        result = operation()

        if transform is not None:
            output_data = transform(result)
        elif isinstance(result, dict):
            output_data = result
        else:
            # If no transform provided and result is not dict, call model_dump if available
            if hasattr(result, 'model_dump'):
                output_data = result.model_dump()
            elif hasattr(result, 'dict'):
                output_data = result.dict()
            else:
                raise TypeError(f"Result type {type(result)} cannot be converted to dict. Provide transform function.")

        output.update(output_data)
        return True

    except ValueError as e:
        output["error"] = str(e)
        return False
    except Exception as e:
        output["error"] = f"Unexpected error: {str(e)}"
        return False


def mt_service_create_output() -> Dict[str, Any]:
    """Create empty output dictionary for service functions.

    Returns:
        Empty dictionary ready for output population

    Example:
        >>> output = mt_service_create_output()
        >>> success = mt_service_execute(some_operation, output)
        >>> if success:
        >>>     return output
        >>> else:
        >>>     raise HTTPException(status_code=400, detail=output["error"])
    """
    return {}
