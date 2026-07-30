"""
Project: AEGIS
Company: Honeydewnuts Nigerian Limited

Purpose:
Basic image loading and inspection service.
"""

from pathlib import Path

import cv2


class ImageProcessingService:

    def load_image(self, image_path: str):

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = cv2.imread(str(path))

        if image is None:
            raise ValueError(
                "Unable to read image."
            )

        return image

    def image_information(self, image):

        height, width = image.shape[:2]

        channels = 1 if len(image.shape) == 2 else image.shape[2]

        return {
            "width": width,
            "height": height,
            "channels": channels
        }
