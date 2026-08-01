"""

Project : AEGIS
System : Autonomous Enterprise Global Intelligence System
Company : Honeydewnuts Nigerian Limited

File : main.py
Version : 2.1.0 - CP-007 Trading Integration

Purpose : FastAPI application entry point.
          Wires all routers including new Trading API.

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging
from app.core.startup import on_startup, on_shutdown

# Existing Routers
from app.api.upload_router import router as upload_router
from app.api.preprocessing_router import router as preprocessing_router
from app.api.chart_detection_router import router as chart_detection_router
from app.api.router import router as base_router

# CP-007 NEW: Trading Router
from app.api.trading_router import router as trading_router

logger = configure_logging(__name__)

app = FastAPI(
    title="AEGIS API",
    description="Autonomous Enterprise Global Intelligence System",
    version="2.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup / Shutdown Events
@app.on_event("startup")
async def startup_event():
    await on_startup()
    logger.info("AEGIS API v2.1.0 Started")

@app.on_event("shutdown")
async def shutdown_event():
    await on_shutdown()
    logger.info("AEGIS API Shut Down")

# ==========================================================
# INCLUDE ALL ROUTERS
# ==========================================================

app.include_router(base_router)
app.include_router(upload_router)
app.include_router(preprocessing_router)
app.include_router(chart_detection_router)

# CP-007 NEW: Trading Execution Endpoints
app.include_router(trading_router)

@app.get("/")
async def root():
    return {
        "service": "AEGIS API",
        "version": "2.1.0",
        "status": "online",
        "modules": ["upload", "preprocessing", "chart_detection", "trading"]
    }
