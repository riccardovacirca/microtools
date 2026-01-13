"""HTTP/API response helper utilities.

This module provides standardized HTTP response helpers and status codes.

Functions follow naming convention: mt_http_<functionality>()
"""

from typing import Any, Dict, List
from .mt_pagination import mt_pagination_create_response


# HTTP Status Code Constants
MT_HTTP_STATUS_OK = 200
MT_HTTP_STATUS_CREATED = 201
MT_HTTP_STATUS_BAD_REQUEST = 400
MT_HTTP_STATUS_NOT_FOUND = 404
MT_HTTP_STATUS_INTERNAL_ERROR = 500


def mt_http_success_response(data: Any, status_code: int = 200, message: str | None = None) -> Dict[str, Any]:
    """Create standardized success response.

    Args:
        data: Response data
        status_code: HTTP status code (default: 200)
        message: Optional success message

    Returns:
        Dictionary with success, data, and optional message

    Example:
        >>> response = mt_http_success_response({"id": 1, "name": "John"})
        >>> # Returns: {"success": True, "data": {"id": 1, "name": "John"}}

        >>> response = mt_http_success_response({"id": 1}, 201, "User created")
        >>> # Returns: {"success": True, "data": {"id": 1}, "message": "User created"}
    """
    response = {
        "success": True,
        "data": data
    }
    if message:
        response["message"] = message
    return response


def mt_http_error_response(error: str, status_code: int = 400, details: Dict | None = None) -> Dict[str, Any]:
    """Create standardized error response.

    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        details: Optional error details dictionary

    Returns:
        Dictionary with success=False, error, and optional details

    Example:
        >>> response = mt_http_error_response("Invalid user ID")
        >>> # Returns: {"success": False, "error": "Invalid user ID"}

        >>> response = mt_http_error_response(
        ...     "Validation failed",
        ...     422,
        ...     {"fields": ["email", "name"]}
        ... )
        >>> # Returns: {
        >>> #     "success": False,
        >>> #     "error": "Validation failed",
        >>> #     "details": {"fields": ["email", "name"]}
        >>> # }
    """
    response = {
        "success": False,
        "error": error
    }
    if details:
        response["details"] = details
    return response


def mt_http_paginated_response(items: List, total: int, page: int, page_size: int) -> Dict[str, Any]:
    """Create standardized paginated response.

    Integrates mt_pagination for complete pagination metadata.

    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (1-indexed)
        page_size: Items per page

    Returns:
        Dictionary with pagination metadata and items

    Example:
        >>> response = mt_http_paginated_response(
        ...     items=[{"id": 1}, {"id": 2}],
        ...     total=100,
        ...     page=1,
        ...     page_size=50
        ... )
        >>> # Returns: {
        >>> #     "items": [...],
        >>> #     "total": 100,
        >>> #     "page": 1,
        >>> #     "page_size": 50,
        >>> #     "total_pages": 2,
        >>> #     "has_next": True,
        >>> #     "has_prev": False
        >>> # }
    """
    return mt_pagination_create_response(items, total, page, page_size)


def mt_http_validate_query_params(params: Dict, allowed: List[str], required: List[str] | None = None) -> None:
    """Validate query parameters.

    Args:
        params: Dictionary of query parameters
        allowed: List of allowed parameter names
        required: Optional list of required parameter names

    Raises:
        ValueError: If validation fails

    Example:
        >>> params = {"page": 1, "limit": 50, "sort": "name"}
        >>> mt_http_validate_query_params(
        ...     params,
        ...     allowed=["page", "limit", "sort"],
        ...     required=["page"]
        ... )  # OK

        >>> params = {"page": 1, "invalid": "foo"}
        >>> mt_http_validate_query_params(
        ...     params,
        ...     allowed=["page", "limit"]
        ... )
        >>> # Raises ValueError: Invalid parameter 'invalid'
    """
    # Check for invalid parameters
    for param in params.keys():
        if param not in allowed:
            raise ValueError(f"Invalid parameter '{param}'")

    # Check for required parameters
    if required:
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter '{param}'")


def mt_http_get_status_text(status_code: int) -> str:
    """Get descriptive text for HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        Descriptive text for status code

    Example:
        >>> text = mt_http_get_status_text(200)
        >>> # Returns: "OK"

        >>> text = mt_http_get_status_text(404)
        >>> # Returns: "Not Found"
    """
    status_texts = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable"
    }
    return status_texts.get(status_code, "Unknown Status")
