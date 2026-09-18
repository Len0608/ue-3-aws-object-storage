"""
Output formatter utility for the AWS Object Storage extension.

Provides:
    format_size          — convert byte count to human-readable string (e.g., '42.5 KB')
    render_objects_table — render a list of S3 object dicts as an ASCII table string
"""
import logging
from typing import Any

from tabulate import tabulate

logger = logging.getLogger("UNV")

# Size unit thresholds in ascending order (largest first for selection logic)
_SIZE_UNITS: list[tuple[int, str]] = [
    (1_099_511_627_776, "TB"),
    (1_073_741_824,     "GB"),
    (1_048_576,         "MB"),
    (1_024,             "KB"),
    (1,                 "B"),
]


def format_size(size_bytes: int) -> str:
    """
    Convert a byte count to a human-readable size string.

    Uses powers of 1024 for unit thresholds. Selects the largest unit where
    the converted value is >= 1.0 and formats to one decimal place.

    Args:
        size_bytes: Non-negative integer byte count.

    Returns:
        Formatted string, e.g. '42.5 KB', '1.2 GB', '512.0 B'.
    """
    logger.debug("Formatting size: %d bytes", size_bytes)
    for threshold, unit in _SIZE_UNITS:
        if size_bytes >= threshold:
            value: float = size_bytes / threshold
            result: str = f"{value:.1f} {unit}"
            logger.debug("Formatted size: %s", result)
            return result
    # size_bytes == 0 falls through; return as bytes
    return f"{size_bytes:.1f} B"


def render_objects_table(objects: list[dict[str, Any]]) -> str:
    """
    Render a list of S3 object metadata dicts as a formatted ASCII table string.

    Each object dict must contain:
        'key'           (str)      — S3 object key
        'size_bytes'    (int)      — object size in bytes
        'last_modified' (str)      — ISO 8601 UTC timestamp string

    Converts size_bytes to human-readable format via format_size before rendering.
    Uses tabulate with tablefmt='rounded_outline'.

    Args:
        objects: List of object dicts as produced by list_s3_objects (with
                 last_modified already converted to an ISO 8601 UTC string).

    Returns:
        The complete rendered ASCII table as a string.
    """
    logger.debug("Rendering ASCII table for %d objects", len(objects))
    rows: list[list[Any]] = [
        [obj["key"], format_size(obj["size_bytes"]), obj["last_modified"]]
        for obj in objects
    ]
    headers: list[str] = ["Object Key", "Size", "Last Modified"]
    table: str = tabulate(rows, headers=headers, tablefmt="rounded_outline")
    logger.debug("ASCII table rendered successfully")
    return table
