"""
AEGIS Main API Router

Autonomous Enterprise Global Intelligence System
Company: Honeydewnuts Nigerian Limited
"""

from fastapi import APIRouter

from app.api.upload_router import router as upload_router

router = APIRouter()

# ------------------------------------------------------------------
# Root API Endpoint
# ------------------------------------------------------------------

@router.get("/")
async def api_root():
    return {
        "application": "AEGIS",
        "description": "Autonomous Enterprise Global Intelligence System",
        "company": "Honeydewnuts Nigerian Limited",
        "version": "0.1.0",
        "status": "Running"
    }


# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "AEGIS Backend",
        "version": "0.1.0"
    }


# ------------------------------------------------------------------
# Image Upload API
# ------------------------------------------------------------------

router.include_router(upload_router)
