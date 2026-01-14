"""Cursor utilities for row-to-dict conversion and recordset manipulation.

This module eliminates the repeated pattern of converting database rows to dictionaries.

Functions follow naming convention: mt_cursor_<functionality>()
"""

from typing import List, Dict, Any


def mt_cursor_row_to_dict(cursor, row) -> Dict[str, Any]:
    """Convert a database row to dictionary using cursor description.

    Eliminates the repeated pattern:
        dict(zip([column[0] for column in cursor.description], row))

    Args:
        cursor: Database cursor with description
        row: Database row tuple

    Returns:
        Dictionary mapping column names to values

    Example:
        >>> with mt_db_cursor() as cursor:
        >>>     cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
        >>>     row = cursor.fetchone()
        >>>     user = mt_cursor_row_to_dict(cursor, row)
        >>>     print(user['name'])  # Access by column name
    """
    if not row:
        return {}
    return dict(zip([column[0] for column in cursor.description], row))


def mt_cursor_rows_to_list(cursor, rows: List[tuple]) -> List[Dict[str, Any]]:
    """Convert multiple database rows to list of dictionaries.

    Args:
        cursor: Database cursor with description
        rows: List of database row tuples

    Returns:
        List of dictionaries mapping column names to values

    Example:
        >>> with mt_db_cursor() as cursor:
        >>>     cursor.execute("SELECT * FROM users")
        >>>     rows = cursor.fetchall()
        >>>     users = mt_cursor_rows_to_list(cursor, rows)
        >>>     for user in users:
        >>>         print(user['name'])
    """
    if not rows:
        return []
    column_names = [column[0] for column in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]


def mt_cursor_to_recordset(cursor) -> List[Dict[str, Any]]:
    """Fetch all rows from cursor and convert to list of dictionaries.

    Combines fetchall() + rows_to_list() in one call.

    Args:
        cursor: Database cursor (after execute)

    Returns:
        List of dictionaries mapping column names to values

    Example:
        >>> with mt_db_cursor() as cursor:
        >>>     cursor.execute("SELECT * FROM users")
        >>>     users = mt_cursor_to_recordset(cursor)
        >>>     for user in users:
        >>>         print(user['name'])
    """
    rows = cursor.fetchall()
    return mt_cursor_rows_to_list(cursor, rows)
