"""
Exceptions module template for UAC Universal Extensions.

This module provides:
- Base ExecutionError class
- Standard exception types (DataValidationError, ConnectionError, etc.)
- ErrorManager singleton for error collection
- Exit code conventions

CUSTOMIZE:
- Add custom exception types for your extension
- Modify ErrorManager methods if needed
"""
from typing import Optional

class ExecutionError(Exception):
    """
    The default error raised by an extension.

    All extension errors must inherit from it.

    Attrs:
        exit_code: The exit code of the extension (for UAC)
        message: The error message for status description
    """

    exit_code: int = 1
    message: str = "Execution Failed"

    def __init__(self, message: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Optional message that will be appended to the default message.

        Note:
            To return result data with errors, use error_manager.set_result()
            before raising the exception.
        """
        if message:
            self.message = f"{self.message}: {message}"

        super().__init__(self.message)

class DataValidationError(ExecutionError):
    """Raised when an input field is invalid."""
    exit_code = 20
    message = "Data Validation Error"

class UnexpectedSystemError(ExecutionError):
    """Raised for unexpected system errors."""
    exit_code = 1
    message = "System Error"

class ValidationError(ExecutionError):
    """
    Raised when a required input field is missing or empty.

    Use this before any API or file system call to signal that the user
    must supply a valid value for a required field. Mapped to exit code 20
    so UAC surfaces it as a user input error.

    Example:
        raise ValidationError("aws_region must not be empty")
    """
    exit_code = 20
    message = "Validation Error"

class AuthenticationError(ExecutionError):
    """
    Raised when AWS credentials are rejected or lack sufficient IAM permissions.

    Covers boto3 ClientError codes: InvalidClientTokenId, SignatureDoesNotMatch,
    AuthFailure, AccessDenied. Signals a user configuration error — the operator
    must supply valid IAM credentials with the required S3 permissions.

    Example:
        raise AuthenticationError("InvalidClientTokenId — check Access Key ID")
    """
    exit_code = 1
    message = "Authentication Error"

class BucketNotFoundError(ExecutionError):
    """
    Raised when the specified S3 bucket does not exist or is inaccessible.

    Covers boto3 ClientError code: NoSuchBucket. Signals that the bucket_name
    field references a bucket that cannot be found under the given credentials
    and region.

    Example:
        raise BucketNotFoundError("Bucket 'my-demo-bucket' does not exist")
    """
    exit_code = 1
    message = "Bucket Not Found"

class RegionEndpointError(ExecutionError):
    """
    Raised when the AWS region is invalid, unreachable, or mismatched with the bucket.

    Covers boto3 ClientError codes: IllegalLocationConstraintException,
    PermanentRedirect; and botocore exceptions: EndpointResolutionError,
    NoRegionError; and DNS/connection failures. Signals that the aws_region field
    is incorrect or the endpoint cannot be reached.

    Example:
        raise RegionEndpointError("Bucket resides in us-west-2, not us-east-1")
    """
    exit_code = 1
    message = "Region Endpoint Error"

class LocalFileNotFoundError(ExecutionError):
    """
    Raised when the local file specified for upload does not exist or is not readable.

    Covers FileNotFoundError and PermissionError when checking the local_file path
    on the UAC agent host. Signals that the operator must correct the local_file
    field value.

    Example:
        raise LocalFileNotFoundError("Local file not found — /data/reports/2026-01-15.csv")
    """
    exit_code = 1
    message = "Local File Not Found"

class S3ApiError(ExecutionError):
    """
    Raised for any S3 ClientError not covered by a more specific exception class.

    Use this as the catch-all for unexpected service-side errors returned by the
    S3 API. The original boto3 error message should be preserved in the detail.

    Example:
        raise S3ApiError(f"Unexpected S3 error: {str(e)}")
    """
    exit_code = 1
    message = "S3 API Error"
