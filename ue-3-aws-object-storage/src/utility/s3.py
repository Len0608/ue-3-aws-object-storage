"""
AWS S3 utility for the AWS Object Storage extension.

Provides:
    create_s3_client   — instantiate a boto3 S3 client with static IAM credentials
    list_s3_objects    — paginate list_objects_v2 and return all object metadata
    upload_s3_file     — upload a local file and return the cleaned ETag
"""
import logging
from typing import Any

import boto3
import botocore.exceptions

from exceptions import (
    AuthenticationError,
    BucketNotFoundError,
    RegionEndpointError,
    S3ApiError,
)

logger = logging.getLogger("UNV")

# boto3 ClientError codes that map to AuthenticationError
_AUTH_ERROR_CODES = frozenset({
    "InvalidClientTokenId",
    "SignatureDoesNotMatch",
    "AuthFailure",
    "AccessDenied",
})

# boto3 ClientError codes that map to RegionEndpointError
_REGION_ERROR_CODES = frozenset({
    "IllegalLocationConstraintException",
    "PermanentRedirect",
})


def _classify_client_error(error: botocore.exceptions.ClientError) -> None:
    """
    Inspect a boto3 ClientError and raise the appropriate custom exception.

    Args:
        error: The ClientError raised by a boto3 S3 API call.

    Raises:
        AuthenticationError: For invalid credentials or insufficient IAM permissions.
        BucketNotFoundError: When the bucket does not exist or is inaccessible.
        RegionEndpointError: For region/endpoint mismatch errors.
        S3ApiError: For any other S3 service-side error.
    """
    code: str = error.response.get("Error", {}).get("Code", "")
    logger.debug("Classifying ClientError code: %s", code)

    if code in _AUTH_ERROR_CODES:
        logger.error("AWS authentication error (%s): %s", code, str(error))
        raise AuthenticationError(str(error))

    if code == "NoSuchBucket":
        logger.error("S3 bucket not found (%s): %s", code, str(error))
        raise BucketNotFoundError(str(error))

    if code in _REGION_ERROR_CODES:
        logger.error("S3 region/endpoint error (%s): %s", code, str(error))
        raise RegionEndpointError(str(error))

    logger.error("Unexpected S3 API error (%s): %s", code, str(error))
    raise S3ApiError(str(error))


def create_s3_client(
    access_key_id: str,
    secret_access_key: str,
    region_name: str,
) -> Any:
    """
    Instantiate and return a boto3 S3 client with static IAM credentials.

    No session token support — STS and IAM instance roles are not used.

    Args:
        access_key_id:     AWS Access Key ID.
        secret_access_key: AWS Secret Access Key.
        region_name:       AWS region identifier (e.g., 'us-east-1').

    Returns:
        A configured boto3 S3 client object.

    Raises:
        RegionEndpointError: If the region cannot be resolved to an endpoint.
    """
    logger.info("Creating S3 client for region: %s", region_name)
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )
        logger.debug("S3 client created successfully")
        return client
    except botocore.exceptions.NoRegionError as exc:
        logger.error("No region specified for S3 client: %s", str(exc))
        raise RegionEndpointError(str(exc))
    except (botocore.exceptions.EndpointResolutionError, Exception) as exc:
        # Catch EndpointResolutionError and DNS/connection failures at client
        # creation time (rare, but possible for obviously invalid region strings).
        if isinstance(exc, (RegionEndpointError,)):
            raise
        error_type = type(exc).__name__
        if "EndpointResolution" in error_type or "NoRegion" in error_type:
            logger.error("S3 endpoint resolution error: %s", str(exc))
            raise RegionEndpointError(str(exc))
        raise


def list_s3_objects(
    s3_client: Any,
    bucket_name: str,
) -> tuple[list[dict[str, Any]], int]:
    """
    Retrieve all objects in an S3 bucket via paginated list_objects_v2 calls.

    Paginates using ContinuationToken until IsTruncated is False. Accumulates
    object metadata (key, size_bytes, last_modified) across all pages.

    Args:
        s3_client:   A boto3 S3 client returned by create_s3_client.
        bucket_name: The name of the S3 bucket to list.

    Returns:
        A tuple of:
            - objects (list[dict]): All objects found. Each dict contains:
                  'key' (str), 'size_bytes' (int), 'last_modified' (datetime).
            - total_count (int): Sum of KeyCount across all pages.

    Raises:
        AuthenticationError: For credential or permission failures.
        BucketNotFoundError: When the bucket does not exist.
        RegionEndpointError: For region/endpoint mismatch or DNS failures.
        S3ApiError: For any other S3 service-side error.
    """
    logger.info("Listing objects in bucket: %s", bucket_name)
    objects: list[dict[str, Any]] = []
    total_count: int = 0
    page_number: int = 0
    kwargs: dict[str, Any] = {"Bucket": bucket_name}

    try:
        while True:
            page_number += 1
            logger.debug("Fetching page %d (ContinuationToken present: %s)",
                         page_number, "NextContinuationToken" in kwargs)

            response: dict[str, Any] = s3_client.list_objects_v2(**kwargs)

            key_count: int = response.get("KeyCount", 0)
            total_count += key_count
            logger.debug("Page %d: KeyCount=%d, IsTruncated=%s",
                         page_number, key_count, response.get("IsTruncated"))

            for obj in response.get("Contents", []):
                objects.append({
                    "key": obj["Key"],
                    "size_bytes": obj["Size"],
                    "last_modified": obj["LastModified"],
                })

            if not response.get("IsTruncated", False):
                break

            kwargs["ContinuationToken"] = response["NextContinuationToken"]

    except botocore.exceptions.ClientError as exc:
        _classify_client_error(exc)
    except botocore.exceptions.EndpointResolutionError as exc:
        logger.error("S3 endpoint resolution error during list: %s", str(exc))
        raise RegionEndpointError(str(exc))
    except botocore.exceptions.NoRegionError as exc:
        logger.error("No region error during list: %s", str(exc))
        raise RegionEndpointError(str(exc))

    logger.info("Completed listing: %d total objects across %d page(s)",
                total_count, page_number)
    return objects, total_count


def upload_s3_file(
    s3_client: Any,
    local_file: str,
    bucket_name: str,
    s3_object_key: str,
) -> str:
    """
    Upload a local file to S3 and return the cleaned ETag of the uploaded object.

    Uses boto3 upload_file (which handles multipart via s3transfer internally),
    then calls head_object to retrieve the ETag. Surrounding double-quote
    characters are stripped from the ETag string as AWS returns them quoted.

    Args:
        s3_client:     A boto3 S3 client returned by create_s3_client.
        local_file:    Absolute path to the local file on the agent host.
        bucket_name:   Target S3 bucket name.
        s3_object_key: Destination object key within the bucket.

    Returns:
        The cleaned ETag string (double-quotes stripped).

    Raises:
        AuthenticationError: For credential or permission failures.
        BucketNotFoundError: When the bucket does not exist.
        RegionEndpointError: For region/endpoint mismatch or DNS failures.
        S3ApiError: For any other S3 service-side error.
    """
    logger.info("Uploading local file to s3://%s/%s", bucket_name, s3_object_key)
    logger.debug("Local file path: %s", local_file)

    try:
        s3_client.upload_file(local_file, bucket_name, s3_object_key)
        logger.info("Upload completed; retrieving ETag via head_object")

        head_response: dict[str, Any] = s3_client.head_object(
            Bucket=bucket_name,
            Key=s3_object_key,
        )
        raw_etag: str = head_response.get("ETag", "")
        etag: str = raw_etag.strip('"')
        logger.debug("ETag retrieved: %s", etag)
        return etag

    except botocore.exceptions.ClientError as exc:
        _classify_client_error(exc)
    except botocore.exceptions.EndpointResolutionError as exc:
        logger.error("S3 endpoint resolution error during upload: %s", str(exc))
        raise RegionEndpointError(str(exc))
    except botocore.exceptions.NoRegionError as exc:
        logger.error("No region error during upload: %s", str(exc))
        raise RegionEndpointError(str(exc))

    # Unreachable — _classify_client_error always raises; satisfy type checker.
    return ""
