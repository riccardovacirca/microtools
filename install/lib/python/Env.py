import os
from typing import Dict

class Env:
  """Environment variables handler."""
  
  def __init__(self):
    """Initialize Env handler."""
    pass
  
  def all(self) -> Dict[str, str]:
    """Get all environment variables as dictionary."""
    return dict(os.environ)
  
  def get(self, key: str, default: str = "") -> str:
    """Get value of specific environment variable."""
    value = os.getenv(key, default)
    # Strip quotes if present
    if value.startswith('"') and value.endswith('"'):
      return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
      return value[1:-1]
    return value
  
  def has(self, key: str) -> bool:
    """Check if environment variable exists."""
    return key in os.environ