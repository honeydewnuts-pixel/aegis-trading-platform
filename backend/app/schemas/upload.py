from datetime import datetime
from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime
    status: str
