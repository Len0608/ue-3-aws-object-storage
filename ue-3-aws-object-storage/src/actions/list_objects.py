"""List Objects action for the AWS Object Storage extension.

Retrieves all objects from the specified S3 bucket via paginated API calls,
displays up to UE_MAX_OUTPUT_RECORDS objects as an ASCII table in STDOUT,
and returns structured object metadata in the Extension Output JSON.
"""

import logging
import os
import sys
from typing import Any, Dict, List

from actions.output import ActionOutput
from exceptions import ValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility.formatter import render_objects_table
from utility.s3 import create_s3_client, list_s3_objects

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()

_DEFAULT_MAX_RECORDS = 100


def list_objects(input_data: InputFields) -> ActionOutput:
    """List objects in an S3 bucket and display them as a formatted ASCII table.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with bucket listing results.

    Raises:
        ValidationError: When a required field is missing or empty.
        AuthenticationError: When AWS credentials are invalid or lack permissions.
        BucketNotFoundError: When the specified bucket does not exist.
        RegionEndpointError: When the region is invalid or unreachable.
        S3ApiError: For unexpected S3 service-side errors.
    """
    logger.info("Starting list_objects action")

    # Initialise OutputFields for real-time UI updates
    output_fields = OutputFields()
    output_fields.update(status="Starting")

    # --- Step 1: Validate required fields ---
    logger.info("Validating required fields")
    missing: List[str] = []
    if not input_data.aws_credentials:
        missing.append("aws_credentials")
    if not input_data.aws_region or input_data.aws_region.value == "":
        missing.append("aws_region")
    if not input_data.bucket_name or input_data.bucket_name.value == "":
        missing.append("bucket_name")

    if missing:
        raise ValidationError(
            f"Required field(s) missing or empty: {', '.join(missing)}"
        )

    aws_region: str = input_data.aws_region.value
    bucket_name: str = input_data.bucket_name.value
    access_key_id: str = input_data.aws_credentials.user
    secret_access_key: str = input_data.aws_credentials.password

    logger.debug(
        "Inputs: aws_region=%s, bucket_name=%s, access_key_id=***",
        aws_region,
        bucket_name,
    )

    # --- Step 2: Read UE_MAX_OUTPUT_RECORDS ---
    max_records: int = _DEFAULT_MAX_RECORDS
    raw_env: str = os.environ.get("UE_MAX_OUTPUT_RECORDS", "")
    if raw_env:
        try:
            parsed: int = int(raw_env)
            if parsed > 0:
                max_records = parsed
            else:
                logger.warning(
                    "UE_MAX_OUTPUT_RECORDS value '%s' is not a positive integer; "
                    "defaulting to %d",
                    raw_env,
                    _DEFAULT_MAX_RECORDS,
                )
        except ValueError:
            logger.warning(
                "UE_MAX_OUTPUT_RECORDS value '%s' is not parseable as an integer; "
                "defaulting to %d",
                raw_env,
                _DEFAULT_MAX_RECORDS,
            )
    logger.debug("UE_MAX_OUTPUT_RECORDS effective value: %d", max_records)

    # --- Step 3: Create S3 client ---
    output_fields.update(status="Connecting to S3")
    logger.info("Creating S3 client for region: %s", aws_region)
    s3_client: Any = create_s3_client(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region_name=aws_region,
    )

    # --- Step 4: Retrieve all objects via pagination ---
    output_fields.update(status="Listing objects")
    logger.info("Retrieving objects from bucket: %s", bucket_name)
    all_objects: List[Dict[str, Any]]
    total_count: int
    all_objects, total_count = list_s3_objects(
        s3_client=s3_client,
        bucket_name=bucket_name,
    )
    logger.info(
        "Retrieved %d total object(s) from bucket '%s'", total_count, bucket_name
    )

    # --- Step 5: Truncate for display ---
    display_objects: List[Dict[str, Any]] = all_objects[:max_records]
    displayed_count: int = len(display_objects)
    truncated: bool = total_count > displayed_count
    logger.debug(
        "Display: %d object(s), total: %d, truncated: %s",
        displayed_count,
        total_count,
        truncated,
    )

    # --- Step 6: Format and print ASCII table ---
    # Convert datetime objects to ISO 8601 UTC strings for display and output
    output_fields.update(status="Formatting output")
    display_for_table: List[Dict[str, Any]] = []
    objects_for_output: List[Dict[str, Any]] = []

    for obj in display_objects:
        last_modified_dt = obj["last_modified"]
        # boto3 returns timezone-aware datetimes; format as ISO 8601 UTC
        last_modified_str: str = last_modified_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        display_for_table.append(
            {
                "key": obj["key"],
                "size_bytes": obj["size_bytes"],
                "last_modified": last_modified_str,
            }
        )
        objects_for_output.append(
            {
                "key": obj["key"],
                "size_bytes": obj["size_bytes"],
                "last_modified": last_modified_str,
            }
        )

    logger.info("Rendering ASCII table for %d object(s)", displayed_count)
    table: str = render_objects_table(objects=display_for_table)
    print(table)

    if truncated:
        print(
            f"Showing {displayed_count} of {total_count} objects. "
            "Set UE_MAX_OUTPUT_RECORDS to retrieve more."
        )
        logger.warning(
            "Result set truncated: displaying %d of %d total object(s). "
            "Set UE_MAX_OUTPUT_RECORDS to retrieve more.",
            displayed_count,
            total_count,
        )
        print(
            f"WARNING: Result set truncated — showing {displayed_count} of "
            f"{total_count} total objects.",
            file=sys.stderr,
        )

    # --- Step 7: Populate output fields and return ---
    output_fields.update(
        status=f"Success: {displayed_count} objects listed",
        object_count=str(displayed_count),
    )

    logger.info(
        "list_objects action completed: %d object(s) listed from '%s'",
        displayed_count,
        bucket_name,
    )

    return ActionOutput(
        bucket=bucket_name,
        object_count=displayed_count,
        total_bucket_count=total_count,
        truncated=truncated,
        objects=objects_for_output,
    )
