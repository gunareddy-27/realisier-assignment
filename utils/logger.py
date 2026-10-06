import logging
import sys
from pathlib import Path
from typing import Optional
from config import LOG_FILE_PATH, LOG_DIR


def setup_logger(
    name: str = "scraper_pipeline",
    log_file: Optional[Path] = LOG_FILE_PATH,
    level: int = logging.INFO
) -> logging.Logger:
    """Configures and returns a logger instance with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if setup_logger is called multiple times
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler (StreamHandler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file:
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
