"""
Project: AEGIS
Company: Honeydewnuts Nigerian Limited

Purpose:
Vision pipeline orchestrator.
"""

from app.services.image_processing_service import ImageProcessingService


class VisionPipelineService:

    def __init__(self):
        self.processor = ImageProcessingService()

    def process_image(self, image_path: str):

        image = self.processor.load_image(image_path)

        info = self.processor.image_information(image)

        return {
            "status": "processed",
            "image": info
        }
