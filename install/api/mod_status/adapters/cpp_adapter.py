"""Adapter for integration with mod_status C++ microservice.

This adapter handles HTTP communication with the external C++ service
and translates responses into Python dictionaries.
"""
import os
import httpx

# Microservice configuration (C++ services on 9000+ ports)
MOD_STATUS_HOST = os.getenv("MOD_STATUS_HOST", "127.0.0.1")
MOD_STATUS_PORT = os.getenv("MOD_STATUS_PORT", "9001")
MOD_STATUS_URL = f"http://{MOD_STATUS_HOST}:{MOD_STATUS_PORT}"


async def get_runtime_info() -> dict:
    """Fetches runtime information from mod_status C++ microservice.
    
    Returns:
        dict: Runtime information including version, uptime, and configuration
        
    Raises:
        httpx.HTTPError: If the C++ service is unreachable or returns an error
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MOD_STATUS_URL}/api/status/info")
        response.raise_for_status()
        return response.json()
