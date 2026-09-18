"""ActionOutput dataclass for action return values."""

import logging
from dataclasses import dataclass
from typing import Optional, Any, Dict, List

logger = logging.getLogger("UNV")


@dataclass
class ActionOutput:
    """Output from action functions.

    Fields cover both List Objects and Upload File action results.
    No stdout_options/output_options control fields are used — all
    available data is always printed and included in Extension Output.

    List Objects fields:
        bucket:             Name of the S3 bucket that was listed.
        object_count:       Number of objects displayed (capped at UE_MAX_OUTPUT_RECORDS).
        total_bucket_count: True total object count across all pages.
        truncated:          True when total_bucket_count > object_count.
        objects:            List of object dicts (key, size_bytes, last_modified ISO string).

    Upload File fields:
        s3_uri:             Full S3 URI of the uploaded object.
        etag:               Cleaned ETag string of the uploaded object.
    """

    # List Objects result fields
    bucket: Optional[str] = None
    object_count: Optional[int] = None
    total_bucket_count: Optional[int] = None
    truncated: Optional[bool] = None
    objects: Optional[List[Dict[str, Any]]] = None

    # Upload File result fields
    s3_uri: Optional[str] = None
    etag: Optional[str] = None

    def print_output(self):
        """Print action results to STDOUT.

        No template control fields exist — all available data is always printed.
        The List Objects action prints its ASCII table directly during execution;
        this method handles the Upload File confirmation line.
        """
        if self.s3_uri is not None:
            print(f"File uploaded successfully to {self.s3_uri}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for Extension Output (unv_output result field).

        No template control fields exist — all non-None fields are always included.

        Returns:
            Dict containing all populated result fields.
        """
        output: Dict[str, Any] = {}

        if self.bucket is not None:
            output["bucket"] = self.bucket

        if self.object_count is not None:
            output["object_count"] = self.object_count

        if self.total_bucket_count is not None:
            output["total_bucket_count"] = self.total_bucket_count

        if self.truncated is not None:
            output["truncated"] = self.truncated

        if self.objects is not None:
            output["objects"] = self.objects

        if self.s3_uri is not None:
            output["s3_uri"] = self.s3_uri

        if self.etag is not None:
            output["etag"] = self.etag

        logger.debug("ActionOutput.to_dict produced %d key(s)", len(output))
        return output
