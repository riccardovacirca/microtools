"""Pagination calculation utilities.

This module standardizes pagination calculations across the application.

Functions follow naming convention: mt_pagination_<functionality>()
"""

from typing import Dict, Any, List


def mt_pagination_calculate_offset(page: int, page_size: int) -> int:
    """Calculate SQL offset from page number and page size.

    Eliminates the repeated pattern: offset = (page - 1) * page_size

    Args:
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        SQL offset value (0-indexed)

    Raises:
        ValueError: If page < 1 or page_size < 1

    Example:
        >>> offset = mt_pagination_calculate_offset(1, 50)  # 0
        >>> offset = mt_pagination_calculate_offset(2, 50)  # 50
        >>> offset = mt_pagination_calculate_offset(3, 50)  # 100
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    return (page - 1) * page_size


def mt_pagination_calculate_pages(total: int, page_size: int) -> int:
    """Calculate total number of pages from total items and page size.

    Args:
        total: Total number of items
        page_size: Items per page

    Returns:
        Total number of pages (rounded up)

    Example:
        >>> mt_pagination_calculate_pages(100, 50)  # 2
        >>> mt_pagination_calculate_pages(101, 50)  # 3
        >>> mt_pagination_calculate_pages(0, 50)    # 0
    """
    if total <= 0:
        return 0
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    return (total + page_size - 1) // page_size


def mt_pagination_validate_params(page: int, page_size: int, max_page_size: int = 1000) -> None:
    """Validate pagination parameters.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum allowed page size

    Raises:
        ValueError: If parameters are invalid

    Example:
        >>> mt_pagination_validate_params(1, 50)  # OK
        >>> mt_pagination_validate_params(0, 50)  # ValueError: page must be >= 1
        >>> mt_pagination_validate_params(1, 2000)  # ValueError: page_size exceeds maximum
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    if page_size > max_page_size:
        raise ValueError(f"page_size exceeds maximum of {max_page_size}")


def mt_pagination_create_response(
    items: List,
    total: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """Create standardized pagination response dictionary.

    Args:
        items: List of items for current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        page_size: Items per page

    Returns:
        Dictionary with pagination metadata and items

    Example:
        >>> response = mt_pagination_create_response(
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
    total_pages = mt_pagination_calculate_pages(total, page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
