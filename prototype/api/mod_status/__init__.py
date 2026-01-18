"""mod_status - Status monitoring module for FastAPI application.

This module provides health check and version information endpoints
by integrating with the C++ mod_status microservice.
"""
from .routes import router

__all__ = ["router"]
