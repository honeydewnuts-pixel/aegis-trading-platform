"""
Project: AEGIS
Company: Honeydewnuts Nigerian Limited

Upload API
"""

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

from app.services.upload_service import UploadService

router = APIRouter(
    prefix="/upload",
    tags=["Image Upload"]
)

service = UploadService()


@router.post("/", response_model=None)
async def upload_image(
    file: UploadFile = File(...)
):

    if not file.content_type.startswith("image/"):

        raise HTTPException(
            status_code=400,
            detail="Only image files are accepted."
        )

    try:

        metadata = await service.save_image(file)

        return metadata.model_dump()

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )
