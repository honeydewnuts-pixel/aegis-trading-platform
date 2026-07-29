from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.upload_service import UploadService

router = APIRouter(
    prefix="/upload",
    tags=["Image Upload"]
)

service = UploadService()


@router.post("/")
async def upload_image(file: UploadFile = File(...)):

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed."
        )

    result = await service.save_image(file)

    return result
