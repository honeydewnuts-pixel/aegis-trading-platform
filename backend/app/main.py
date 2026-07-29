from fastapi import FastAPI

from app.config import settings
from app.api.router import router
from app.core.startup import startup_message, shutdown_message

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.include_router(router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def on_startup():
    startup_message()


@app.on_event("shutdown")
async def on_shutdown():
    shutdown_message()


@app.get("/")
async def application_root():
    return {
        "message": "Welcome to AEGIS",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": "Honeydewnuts Nigerian Limited",
    }
