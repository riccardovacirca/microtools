from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Environment variables are already exported by 'wa ag start'
# No need to load .env manually

# Import module routers
from mod_status.routes import router as status_router
from mod_contatti.routes import router as contatti_router

app = FastAPI(
    title=os.getenv("PROJECT_NAME", "microservice"),
    version=os.getenv("VERSION", "1.0.0"),
    description="FastAPI Microservice Gateway"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register module routers
app.include_router(status_router, prefix="/api/status", tags=["status"])
app.include_router(contatti_router)
