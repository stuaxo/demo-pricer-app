import logging
import os


def configure_logging():
    if os.environ.get("DEBUG_AIOSQLITE", "N").lower() in ["1", "true", "yes"]:
        logging.basicConfig(level=logging.DEBUG)
        aiosqlite_logger = logging.getLogger("aiosqlite")
        aiosqlite_logger.setLevel(logging.DEBUG)
