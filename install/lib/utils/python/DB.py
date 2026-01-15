from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from .DBConnPool import DBConnPool

class Record(Dict[str, Any]):
  """Wrapper for single database record."""
  pass

class Recordset(List[Record]):
  """Wrapper for list of database records."""
  pass

class DB:
  """Database connection and query handler with connection pool support."""
  
  def __init__(self):
    """Initialize DB handler."""
    self.connection = None
    self.cursor = None
    self.pool = None
    self._cursor_result = None
    self._current_row_index = 0
    self._last_rowcount = 0
    self.cursor_first_call = True
    self.cursor_has_data = False
  
  def acquire(self, pool: DBConnPool):
    """
    Acquire connection from pool.
    
    Args:
      pool: DBConnPool instance
    """
    if self.connection is not None:
      raise RuntimeError("Already connected")
    
    self.pool = pool
    self.connection = pool.acquire()
  
  def release(self):
    """Release connection back to pool."""
    if self.connection is None:
      return
    
    self.disconnect()  # Clean up any active cursor
    if self.pool:
      self.pool.release(self.connection)
    
    self.connection = None
    self.pool = None
  
  def disconnect(self):
    """Disconnect from database."""
    self.cursor_close()
    # Connection remains in pool, will be released via release()
  
  def is_connected(self) -> bool:
    """Check if connected to database."""
    return self.connection is not None and self.pool is not None
  
  def query(self, sql: str, params: Optional[tuple]) -> int:
    """
    Execute a SQL query that modifies data.

    Args:
      sql: SQL query (INSERT, UPDATE, DELETE)
      params: Query parameters or None

    Returns:
      Number of affected rows
    """
    if not self.is_connected():
      raise RuntimeError("Not connected to database")

    with self._get_cursor() as cursor:
      if params:
        cursor.execute(sql, params)
      else:
        cursor.execute(sql)
      self._last_rowcount = cursor.rowcount
      return cursor.rowcount

  def insert(self, sql: str, params: Optional[tuple]) -> int:
    """
    Execute INSERT query and return last inserted ID.

    Args:
      sql: SQL INSERT query
      params: Query parameters or None

    Returns:
      Last inserted row ID
    """
    if not self.is_connected():
      raise RuntimeError("Not connected to database")

    with self._get_cursor() as cursor:
      if params:
        cursor.execute(sql, params)
      else:
        cursor.execute(sql)
      cursor.execute("SELECT last_insert_rowid()")
      row = cursor.fetchone()
      return row[0] if row else 0
  
  def select(self, sql: str, params: Optional[tuple]) -> Record:
    """
    Execute SELECT query and return first row.

    Args:
      sql: SQL SELECT query
      params: Query parameters or None

    Returns:
      First record as Record
    """
    if not self.is_connected():
      raise RuntimeError("Not connected to database")

    with self._get_cursor() as cursor:
      if params:
        cursor.execute(sql, params)
      else:
        cursor.execute(sql)

      row = cursor.fetchone()
      if not row:
        return Record()

      return self._row_to_dict(cursor, row)
  
  def select_all(self, sql: str, params: Optional[tuple]) -> Recordset:
    """
    Execute SELECT query and return all rows.

    Args:
      sql: SQL SELECT query
      params: Query parameters or None

    Returns:
      All records as Recordset
    """
    if not self.is_connected():
      raise RuntimeError("Not connected to database")

    with self._get_cursor() as cursor:
      if params:
        cursor.execute(sql, params)
      else:
        cursor.execute(sql)

      rows = cursor.fetchall()
      return self._rows_to_list(cursor, rows)
  
  def cursor_open(self, sql: str, params: Optional[tuple]):
    """
    Open cursor for iterating through query results.

    Args:
      sql: SQL SELECT query
      params: Query parameters or None
    """
    if not self.is_connected():
      raise RuntimeError("Not connected to database")

    self.cursor_close()  # Close any existing cursor

    self.cursor = self.connection.cursor()
    if params:
      self.cursor.execute(sql, params)
    else:
      self.cursor.execute(sql)

    self._cursor_result = self.cursor.fetchall()
    self.cursor_first_call = True
    self.cursor_has_data = len(self._cursor_result) > 0
    self._current_row_index = 0
  
  def cursor_has_next(self) -> bool:
    """Check if cursor has more rows available."""
    if not self.cursor_has_data:
      return False
    
    return self._current_row_index < len(self._cursor_result)
  
  def cursor_next(self) -> Record:
    """Retrieve next row from cursor."""
    if not self.cursor_has_data or not self.cursor_has_next():
      return Record()
    
    row = self._cursor_result[self._current_row_index]
    self._current_row_index += 1
    
    if self.cursor_first_call:
      self.cursor_first_call = False
    
    return self._row_to_dict(self.cursor, row)
  
  def cursor_close(self):
    """Close cursor and release resources."""
    if self.cursor:
      try:
        self.cursor.close()
      except:
        pass
    
    self.cursor = None
    self._cursor_result = None
    self.cursor_first_call = True
    self.cursor_has_data = False
    self._current_row_index = 0
  
  @contextmanager
  def _get_cursor(self):
    """Context manager for cursor operations."""
    cursor = self.connection.cursor()
    try:
      yield cursor
      self.connection.commit()
    except Exception:
      self.connection.rollback()
      raise
    finally:
      cursor.close()
  
  def _row_to_dict(self, cursor, row) -> Record:
    """Convert database row to Record dictionary."""
    if not row:
      return Record()
    return Record(zip([column[0] for column in cursor.description], row))
  
  def _rows_to_list(self, cursor, rows) -> Recordset:
    """Convert database rows to Recordset list."""
    if not rows:
      return Recordset()
    column_names = [column[0] for column in cursor.description]
    return Recordset([Record(zip(column_names, row)) for row in rows])
  
  def __enter__(self):
    return self
  
  def __exit__(self, exc_type, exc_val, exc_tb):
    self.release()