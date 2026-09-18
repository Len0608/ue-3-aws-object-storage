"""
Utility package for the AWS Object Storage extension.

Modules:
    s3        — boto3 S3 client creation, object listing, file upload, error classification
    formatter — human-readable size formatting and ASCII table rendering
"""
from utility.s3 import create_s3_client, list_s3_objects, upload_s3_file
from utility.formatter import format_size, render_objects_table
