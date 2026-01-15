import os
from typing import Dict
from pathlib import Path

class Env:
  """Environment variables handler with .env file support."""

  _loaded = False

  def __init__(self, env_path: str = "/workspace/.env"):
    """Initialize Env handler and load .env file.

    Args:
      env_path: Path to .env file (default: /workspace/.env)
    """
    if not Env._loaded:
      self._load_env_file(env_path)
      Env._loaded = True

  def _load_env_file(self, env_path: str):
    """Load environment variables from .env file."""
    path = Path(env_path)
    if not path.exists():
      return
    with open(path, 'r') as f:
      for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
          continue
        if '=' not in line:
          continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
          value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
          value = value[1:-1]
        if key and key not in os.environ:
          os.environ[key] = value
  
  def all(self) -> Dict[str, str]:
    """Get all environment variables as dictionary."""
    return dict(os.environ)
  
  def get(self, key: str, default: str = "") -> str:
    """Get value of specific environment variable."""
    value = os.getenv(key, default)
    # Convert to string if not already
    if not isinstance(value, str):
      return str(value)
    # Strip quotes if present
    if value.startswith('"') and value.endswith('"'):
      return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
      return value[1:-1]
    return value
  
  def has(self, key: str) -> bool:
    """Check if environment variable exists."""
    return key in os.environ