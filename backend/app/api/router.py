from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {
        "application": "AEGIS",
        "status": "Running",
        "version": "0.1.0",
        "company": "Honeydewnuts Nigerian Limited"
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }
