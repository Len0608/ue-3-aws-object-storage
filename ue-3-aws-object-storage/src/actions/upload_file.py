"""Upload File action for the AWS Object Storage extension.

Uploads a local file from the UAC agent host to the specified S3 bucket
and object key, then retrieves the ETag via a follow-up HEAD request.
Returns the S3 URI and ETag in the Extension Output JSON.
"""

import logging
from pathlib import Path
from typing import Any, List

from actions.output import ActionOutput
from exceptions import LocalFileNotFoundError, ValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility.s3 import create_s3_client, upload_s3_file

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()


def upload_file(input_data: InputFields) -> ActionOutput:
    """Upload a local file to an S3 bucket.

    Validates required fields and local file existence, creates an S3 client,
    uploads the file, retrieves the ETag, and returns the S3 URI and ETag.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with upload results including s3_uri and etag.

    Raises:
        ValidationError: When a required field is missing or empty.
        LocalFileNotFoundError: When the local file does not exist or is not readable.
        AuthenticationError: When AWS credentials are invalid or lack permissions.
        BucketNotFoundError: When the specified bucket does not exist.
        RegionEndpointError: When the region is invalid or unreachable.
        S3ApiError: For unexpected S3 service-side errors.
    """
    logger.info("Starting upload_file action")

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
    if not input_data.local_file or input_data.local_file.value == "":
        missing.append("local_file")
    if not input_data.s3_object_key or input_data.s3_object_key.value == "":
        missing.append("s3_object_key")

    if missing:
        raise ValidationError(
            f"Required field(s) missing or empty: {', '.join(missing)}"
        )

    aws_region: str = input_data.aws_region.value
    bucket_name: str = input_data.bucket_name.value
    local_file: str = input_data.local_file.value
    s3_object_key: str = input_data.s3_object_key.value
    access_key_id: str = input_data.aws_credentials.user
    secret_access_key: str = input_data.aws_credentials.password

    logger.debug(
        "Inputs: aws_region=%s, bucket_name=%s, local_file=%s, "
        "s3_object_key=%s, access_key_id=***",
        aws_region,
        bucket_name,
        local_file,
        s3_object_key,
    )

    # --- Step 2: Check local file existence ---
    output_fields.update(status="Checking local file")
    logger.info("Checking local file existence: %s", local_file)
    local_path = Path(local_file)

    try:
        if not local_path.is_file():
            logger.error("Local file does not exist or is not a regular file: %s", local_file)
            raise LocalFileNotFoundError(
                f"Local file not found — {local_file}"
            )
    except PermissionError:
        logger.error("Permission denied reading local file: %s", local_file)
        raise LocalFileNotFoundError(
            f"Local file not found — {local_file}"
        )

    logger.debug("Local file exists and is accessible: %s", local_file)

    # --- Step 3: Create S3 client ---
    output_fields.update(status="Connecting to S3")
    logger.info("Creating S3 client for region: %s", aws_region)
    s3_client: Any = create_s3_client(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region_name=aws_region,
    )

    # --- Step 4: Upload the file and Step 5: Retrieve ETag ---
    output_fields.update(status="Uploading file")
    logger.info(
        "Uploading '%s' to s3://%s/%s", local_file, bucket_name, s3_object_key
    )
    etag: str = upload_s3_file(
        s3_client=s3_client,
        local_file=local_file,
        bucket_name=bucket_name,
        s3_object_key=s3_object_key,
    )
    logger.info("File uploaded successfully; ETag: %s", etag)

    # --- Step 6: Build S3 URI ---
    s3_uri: str = f"s3://{bucket_name}/{s3_object_key}"
    logger.debug("S3 URI: %s", s3_uri)

    # --- Step 7: Populate output fields ---
    output_fields.update(
        status=f"Success: File uploaded to {s3_uri}",
        s3_uri=s3_uri,
    )

    logger.info("upload_file action completed: %s", s3_uri)

    return ActionOutput(
        s3_uri=s3_uri,
        etag=etag,
    )
