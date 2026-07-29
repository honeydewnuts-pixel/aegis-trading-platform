"""
Application startup events.
"""

import logging

logger = logging.getLogger("AEGIS")


def startup_message():
    logger.info("========================================")
    logger.info("AEGIS Backend Starting...")
    logger.info("Company: Honeydewnuts Nigerian Limited")
    logger.info("Status: Development")
    logger.info("========================================")


def shutdown_message():
    logger.info("AEGIS Backend Stopped")
