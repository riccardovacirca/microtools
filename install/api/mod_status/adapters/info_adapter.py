import os
import httpx
from typing import Dict, Any

# Config microservizio C++
MOD_STATUS_HOST = os.getenv("MOD_STATUS_HOST", "127.0.0.1")
MOD_STATUS_PORT = os.getenv("MOD_STATUS_PORT", "9001")
MOD_STATUS_URL = f"http://{MOD_STATUS_HOST}:{MOD_STATUS_PORT}"

async def get() -> Dict[str, Any]:
    """Recupera info status da microservizio C++."""
    async with httpx.AsyncClient() as client:
        retv = await client.get(f"{MOD_STATUS_URL}/api/status/info")
        retv.raise_for_status()
        return retv.json()
