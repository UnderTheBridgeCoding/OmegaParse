"""
Utility functions for OmegaParser.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import logging


# Timestamp formats to try when parsing
TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
    "%Y-%m-%dT%H:%M:%SZ",      # ISO format without microseconds
    "%Y-%m-%d %H:%M:%S",       # Standard datetime
    "%Y-%m-%d",                 # Date only
    "%Y-%m-%dT%H:%M:%S",       # ISO without Z
]

# Maximum characters to preserve from HTML/TXT content
MAX_RAW_CONTENT_LENGTH = 1000


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging for OmegaParser.
    """
    logger = logging.getLogger("omegaparser")
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def generate_record_id(file_path: str, index: int) -> str:
    """
    Generate a deterministic record ID based on file path and index.
    """
    content = f"{file_path}:{index}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def safe_json_load(file_path: Path) -> Optional[Any]:
    """
    Attempt to load JSON from a file, returning None on failure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.getLogger("omegaparser").debug(
            f"Failed to parse JSON from {file_path}: {e}"
        )
        return None


def parse_timestamp(timestamp_str: str) -> tuple[Optional[datetime], bool]:
    """
    Attempt to parse a timestamp string into a datetime object.
    
    Returns:
        tuple: (datetime object or None, uncertainty flag)
    """
    if not timestamp_str:
        return None, True
    
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(timestamp_str, fmt), False
        except ValueError:
            continue
    
    # Could not parse - uncertain
    return None, True


def ensure_output_dir(output_path: Path) -> None:
    """
    Ensure the output directory exists.
    """
    output_path.mkdir(parents=True, exist_ok=True)


def get_file_extension(file_path: Path) -> str:
    """
    Get the lowercase file extension without the dot.
    """
    return file_path.suffix.lstrip('.').lower()
