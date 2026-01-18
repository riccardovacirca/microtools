import os
from typing import Dict
from pathlib import Path

class Env:
    """Environment variables handler with .env file support."""

    _loaded = False

    def __init__(self, envPath: str):
        """Initialize Env handler and load .env file."""
        if not Env._loaded:
            self._loadEnvFile(envPath)
            Env._loaded = True

    def _loadEnvFile(self, envPath: str):
        """Load environment variables from .env file."""
        path = Path(envPath)
        if path.exists():
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    idx = line.index("=")
                    key = line[:idx].strip()
                    value = line[idx + 1:].strip()
                    value = self._stripQuotes(value)
                    if key and key not in os.environ:
                        os.environ[key] = value

    def _stripQuotes(self, value: str) -> str:
        """Remove surrounding quotes from value."""
        retv = value
        if len(retv) >= 2:
            if retv.startswith('"') and retv.endswith('"'):
                retv = retv[1:-1]
            elif retv.startswith("'") and retv.endswith("'"):
                retv = retv[1:-1]
        return retv

    def getAll(self) -> Dict[str, str]:
        """Get all environment variables as dictionary."""
        retv = {}
        for key in os.environ:
            retv[key] = os.environ[key]
        return retv

    def get(self, key: str, default: str) -> str:
        """Get value of specific environment variable."""
        retv = os.getenv(key, default)
        if not isinstance(retv, str):
            retv = str(retv)
        retv = self._stripQuotes(retv)
        return retv

    def has(self, key: str) -> bool:
        """Check if environment variable exists."""
        return key in os.environ
