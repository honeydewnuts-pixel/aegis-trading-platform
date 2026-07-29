from fastapi import FastAPI

from app.config import settings
from app.api.router import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/")
async def application_root():
    return {
        "message": "Welcome to AEGIS",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
