from pathlib import Path
from datetime import datetime
from fastapi import UploadFile

UPLOAD_DIRECTORY = Path("uploads")


class UploadService:

    def __init__(self):
        UPLOAD_DIRECTORY.mkdir(exist_ok=True)

    async def save_image(self, file: UploadFile):

        destination = UPLOAD_DIRECTORY / file.filename

        contents = await file.read()

        destination.write_bytes(contents)

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
            "uploaded_at": datetime.utcnow(),
            "status": "uploaded"
        }
