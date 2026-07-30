"""
Project: AEGIS
Company: Honeydewnuts Nigerian Limited

Purpose:
Schema returned after image preprocessing.
"""

from pydantic import BaseModel


class ImageProcessingResponse(BaseModel):

    status: str

    image: dict
