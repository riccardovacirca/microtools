"""Query building helper utilities.

This module provides helpers for building SQL queries with common patterns
like soft delete filtering, dynamic update clauses, and search patterns.

Functions follow naming convention: mt_query_<functionality>()
"""

from typing import List, Tuple, Any, Dict


def mt_query_add_soft_delete_filter(
    query: str,
    include_deleted: bool = False,
    where_exists: bool = False
) -> str:
    """Add soft delete filter to SQL query.

    Eliminates the repeated pattern:
        if not include_deleted:
            query += " AND deleted_at IS NULL"

    Args:
        query: Base SQL query
        include_deleted: If False, adds deleted_at IS NULL filter
        where_exists: If False, adds WHERE clause; if True, adds AND clause

    Returns:
        Query with soft delete filter appended

    Example:
        >>> query = "SELECT * FROM users"
        >>> query = mt_query_add_soft_delete_filter(query, include_deleted=False)
        >>> # Returns: "SELECT * FROM users WHERE deleted_at IS NULL"

        >>> query = "SELECT * FROM users WHERE active = 1"
        >>> query = mt_query_add_soft_delete_filter(query, where_exists=True)
        >>> # Returns: "SELECT * FROM users WHERE active = 1 AND deleted_at IS NULL"
    """
    if not include_deleted:
        if where_exists:
            query += " AND deleted_at IS NULL"
        else:
            query += " WHERE deleted_at IS NULL"
    return query


def mt_query_build_update_clause(
    updates: Dict[str, Any],
    allowed_fields: List[str] | None = None
) -> Tuple[str, List[Any]]:
    """Build dynamic UPDATE clause from dictionary of field updates.

    Eliminates the repeated pattern of building UPDATE clauses with conditional fields.

    Args:
        updates: Dictionary of field: value pairs to update
        allowed_fields: Optional list of allowed field names (for security)

    Returns:
        Tuple of (SET clause string, parameter values list)

    Raises:
        ValueError: If no valid updates or field not allowed

    Example:
        >>> updates = {"name": "John", "email": "john@example.com", "age": None}
        >>> set_clause, params = mt_query_build_update_clause(updates)
        >>> # Returns: ("name = ?, email = ?, age = ?", ["John", "john@example.com", None])
        >>>
        >>> query = f"UPDATE users SET {set_clause} WHERE id = ?"
        >>> params.append(user_id)
        >>> cursor.execute(query, params)
    """
    if not updates:
        raise ValueError("No updates provided")

    set_parts = []
    params = []

    for field, value in updates.items():
        # Security check
        if allowed_fields is not None and field not in allowed_fields:
            raise ValueError(f"Field '{field}' not allowed for update")

        set_parts.append(f"{field} = ?")
        params.append(value)

    if not set_parts:
        raise ValueError("No valid updates after filtering")

    return ", ".join(set_parts), params


def mt_query_build_search_pattern(query: str, fuzzy: bool = True) -> str:
    """Build SQL LIKE pattern from search query.

    Args:
        query: Search query string
        fuzzy: If True, adds % wildcards for fuzzy matching

    Returns:
        SQL LIKE pattern string

    Example:
        >>> pattern = mt_query_build_search_pattern("john")
        >>> # Returns: "%john%"
        >>> cursor.execute("SELECT * FROM users WHERE name LIKE ?", (pattern,))

        >>> pattern = mt_query_build_search_pattern("john", fuzzy=False)
        >>> # Returns: "john"
    """
    if not query:
        return "%"

    # Escape SQL LIKE special characters
    escaped = query.replace("%", "\\%").replace("_", "\\_")

    if fuzzy:
        return f"%{escaped}%"
    return escaped


def mt_query_build_multi_field_search(
    query: str,
    fields: List[str],
    operator: str = "OR"
) -> Tuple[str, List[str]]:
    """Build multi-field search condition.

    Args:
        query: Search query string
        fields: List of field names to search
        operator: SQL operator (OR or AND)

    Returns:
        Tuple of (WHERE condition string, list of pattern parameters)

    Example:
        >>> condition, params = mt_query_build_multi_field_search(
        ...     "john",
        ...     ["name", "email", "company"]
        ... )
        >>> # Returns: ("name LIKE ? OR email LIKE ? OR company LIKE ?", ["%john%", "%john%", "%john%"])
        >>>
        >>> sql = f"SELECT * FROM users WHERE {condition}"
        >>> cursor.execute(sql, params)
    """
    if not fields:
        raise ValueError("No fields provided for search")

    pattern = mt_query_build_search_pattern(query)
    conditions = [f"{field} LIKE ?" for field in fields]
    where_clause = f" {operator} ".join(conditions)
    params = [pattern] * len(fields)

    return where_clause, params
