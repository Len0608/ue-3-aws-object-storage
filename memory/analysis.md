# AWS Object Storage - Implementation Analysis

**Extension Name:** AWS Object Storage (ue-3-aws-object-storage)
**Universal Template Name:** AWS Object Storage
**Target Platform:** Linux

---

## Extension Overview

The AWS Object Storage extension provides an MVP/demo AWS S3 integration for Stonebranch UAC. It exposes two core operations: listing objects in a specified S3 bucket (with a capped, paginated result set displayed as a formatted ASCII table) and uploading a local file from the UAC agent host to a specified S3 bucket and object key. Authentication is exclusively via static IAM credentials (Access Key ID + Secret Access Key) supplied through a single UAC Credential entity. All boto3 dependencies are bundled with the extension; no AWS tooling is required on the agent host.

---

# Template Fields

## 1. Input Fields

**action**
- **Type**: Choice Field (Single-select)
- **Required When**: always
- **Options**:
  - List Objects — Retrieves and displays the list of objects in the specified S3 bucket as an ASCII table
  - Upload File — Uploads a local file from the UAC agent host to the specified S3 bucket and object key
- **Default Value**: List Objects
- **Validation**:
  - Must be one of the defined options
- **Purpose**: Selects the S3 operation to perform

**aws_credentials**
- **Type**: Credential Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must reference a valid UAC Credential entity
  - `user` attribute maps to AWS Access Key ID
  - `password` attribute maps to AWS Secret Access Key
- **Purpose**: Provides AWS IAM static credentials for authenticating with the S3 API. The `user` attribute holds the Access Key ID; the `password` attribute holds the Secret Access Key. Session tokens (STS) and IAM instance roles are not supported.

**aws_region**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Default Value**: `us-east-1`
- **Validation**:
  - Must be a non-empty string
- **Purpose**: The AWS region identifier where the target S3 bucket resides
- **Example**: `us-east-1`

**bucket_name**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must be a non-empty string
- **Purpose**: The name of the AWS S3 bucket to operate on
- **Example**: `my-demo-bucket`

**local_file**
- **Type**: Text Field
- **Visible When**: action value is equal to "Upload File". It is required when it's visible.
- **Required When**: action value is equal to "Upload File"
- **Validation**:
  - Must be a non-empty string
- **Purpose**: The absolute path of the file on the UAC agent host file system to upload to S3
- **Example**: `/data/reports/2026-01-15.csv`

**s3_object_key**
- **Type**: Text Field
- **Visible When**: action value is equal to "Upload File". It is required when it's visible.
- **Required When**: action value is equal to "Upload File"
- **Validation**:
  - Must be a non-empty string
  - Must not begin with a leading forward slash
- **Purpose**: The destination object key (path and filename) within the S3 bucket where the file will be stored
- **Example**: `reports/2026-01-15.csv`

---

## 2. Output Fields

**status**
- **Type**: Text Output
- **Purpose**: Short human-readable summary of the action result. Always populated on both success and failure.
- **Examples**: `"Success: 42 objects listed"`, `"Success: File uploaded to s3://my-demo-bucket/reports/2026-01-15.csv"`, `"Error: Authentication failed — InvalidClientTokenId"`

**object_count**
- **Type**: Text Output
- **Visible When**: action is "List Objects"
- **Purpose**: The number of S3 objects returned by the List Objects action (capped at UE_MAX_OUTPUT_RECORDS)
- **Examples**: `"42"`, `"100"`

**s3_uri**
- **Type**: Text Output
- **Visible When**: action is "Upload File"
- **Purpose**: The full S3 URI of the uploaded object, populated on successful Upload File completion
- **Examples**: `"s3://my-demo-bucket/reports/2026-01-15.csv"`

---

## 3. Field Ordering

The task form uses a **2-column grid layout**. Fields can be displayed in two ways:

- **Full-width fields**: Span both columns (typically for dropdowns, credentials, or primary selections)
- **Half-width fields**: Occupy one column, allowing two fields side-by-side (typically for related pairs)

**Layout Rules:**
- Credential fields ALWAYS span full-width (both columns)
- Group related fields side-by-side when logical (e.g., country/city, latitude/longitude)
- Primary selection fields typically span full-width for prominence

**Field Order (Visual Layout):**

```
┌─────────────────────────────────────────────┐
│                   action                    │  ← Full-width
├─────────────────────────────────────────────┤
│               aws_credentials               │  ← Full-width (credential)
├──────────────────────┬──────────────────────┤
│      aws_region      │     bucket_name      │  ← Half-width pair
├─────────────────────────────────────────────┤
│                  local_file                 │  ← Full-width (Upload File only)
├─────────────────────────────────────────────┤
│                 s3_object_key               │  ← Full-width (Upload File only)
├─────────────────────────────────────────────┤
│                    status                   │  ← Full-width (output only)
├─────────────────────────────────────────────┤
│                 object_count                │  ← Full-width (output only)
├─────────────────────────────────────────────┤
│                    s3_uri                   │  ← Full-width (output only)
└─────────────────────────────────────────────┘
```

---

# Actions

## Action 1: List Objects

**Description**: Connects to the specified AWS S3 bucket using the provided static credentials and AWS region, retrieves the full list of objects via paginated API calls, and displays up to `UE_MAX_OUTPUT_RECORDS` objects as a formatted ASCII table in STDOUT. Structured per-object metadata is returned in the Extension Output JSON. A truncation note is appended to STDOUT when the total object count exceeds the cap.

### Input Requirements

- **action** — must be "List Objects"
- **aws_credentials** — provides AWS Access Key ID (`user`) and Secret Access Key (`password`)
- **aws_region** — AWS region identifier for the target bucket
- **bucket_name** — name of the S3 bucket to list

### Execution Flow

**Step 1: Validate required fields**
- Confirm that `aws_credentials`, `aws_region`, and `bucket_name` are all non-empty.
- If any required field is missing or empty, raise `ValidationError` with exit code 20 and a descriptive status message. No S3 API call is made.

**Step 2: Read UE_MAX_OUTPUT_RECORDS**
- Read the `UE_MAX_OUTPUT_RECORDS` environment variable.
- Parse its value as a positive integer. If not set, not parseable, or not a positive integer, default to `100`.

**Step 3: Create S3 client**
- Instantiate a boto3 S3 client using:
  - `aws_credentials["user"]` as the AWS Access Key ID
  - `aws_credentials["password"]` as the AWS Secret Access Key
  - `aws_region` as the `region_name`
- No session token is used.

**Step 4: Retrieve all objects via pagination**
- Call `list_objects_v2` with `Bucket=bucket_name`.
- Paginate using the `ContinuationToken` returned in each response until `IsTruncated` is `False`.
- For every page, collect each object's `Key` (string), `Size` (integer bytes), and `LastModified` (UTC datetime) from the `Contents` list. Accumulate all collected objects across all pages into a single list.
- Track the total object count across all pages as the sum of `KeyCount` per page.
- If a boto3 `ClientError` is raised during any API call, classify the error code and raise the appropriate custom exception (see Exception Mapping Strategy). Wrap `EndpointResolutionError` and DNS/connection failures as `RegionEndpointError`.

**Step 5: Truncate for display**
- The `display_objects` list = the first `UE_MAX_OUTPUT_RECORDS` objects from the full collected list.
- `total_count` = total object count across all pages.
- `displayed_count` = length of `display_objects`.

**Step 6: Format and print ASCII table**
- Convert each object's `Size` bytes to a human-readable string using the size formatter (see Output Formatter Utility).
- Convert each object's `LastModified` datetime to an ISO 8601 UTC string (e.g., `2026-01-15T08:22:10Z`).
- Render `display_objects` as an ASCII table using `tabulate` with:
  - `tablefmt="rounded_outline"`
  - Column headers: `Object Key`, `Size`, `Last Modified`
- Print the rendered table to STDOUT.
- If `total_count > displayed_count`, print this note to STDOUT immediately after the table:
  `Showing <displayed_count> of <total_count> objects. Set UE_MAX_OUTPUT_RECORDS to retrieve more.`
- If `total_count > displayed_count`, also emit a warning to STDERR indicating truncation.

**Step 7: Populate output fields and return Extension Output**
- Set `output_data.status` = `Success: <displayed_count> objects listed`
- Set `output_data.object_count` = string representation of `displayed_count`
- Return Extension Output `result` containing:
  - `bucket`: the `bucket_name` string
  - `object_count`: `displayed_count` as integer
  - `total_bucket_count`: `total_count` as integer
  - `truncated`: boolean `True` if `total_count > displayed_count`, else `False`
  - `objects`: list of dicts for each object in `display_objects`, each containing `key` (string), `size_bytes` (integer), `last_modified` (ISO 8601 UTC string)
- Return exit code 0.

### Output Examples

**STDOUT**:
```
╭──────────────────────────────────┬──────────┬──────────────────────────╮
│ Object Key                       │ Size     │ Last Modified            │
├──────────────────────────────────┼──────────┼──────────────────────────┤
│ reports/2026-01-15.csv           │ 42.5 KB  │ 2026-01-15T08:22:10Z     │
│ logs/app-2026-01-14.log          │ 1.2 GB   │ 2026-01-14T23:59:55Z     │
╰──────────────────────────────────┴──────────┴──────────────────────────╯
Showing 100 of 342 objects. Set UE_MAX_OUTPUT_RECORDS to retrieve more.
```

**Extension Output result object (JSON)**:

The Extension output also includes `exit_code`, `status_description`, and `invocation` elements added automatically during implementation.

```json
{
  "result": {
    "bucket": "my-demo-bucket",
    "object_count": 42,
    "total_bucket_count": 42,
    "truncated": false,
    "objects": [
      {
        "key": "reports/2026-01-15.csv",
        "size_bytes": 43520,
        "last_modified": "2026-01-15T08:22:10Z"
      }
    ]
  }
}
```

### Success Criteria

1. The S3 bucket is accessible with the provided credentials and region.
2. The object list is retrieved and displayed as a formatted ASCII table in STDOUT.
3. Return code is 0.
4. Extension Output JSON `result` contains `bucket`, `object_count`, `total_bucket_count`, `truncated`, and `objects` array.
5. Output field `status` = `Success: <N> objects listed`.
6. Output field `object_count` = string representation of N.
7. When `total_bucket_count > object_count`, the truncation note is present in STDOUT.

---

## Action 2: Upload File

**Description**: Connects to the specified AWS S3 bucket using the provided static credentials and AWS region, verifies the local file exists on the agent host, uploads it to the specified S3 object key, retrieves the ETag via a follow-up HEAD request, and returns the S3 URI and ETag in the Extension Output JSON.

### Input Requirements

- **action** — must be "Upload File"
- **aws_credentials** — provides AWS Access Key ID (`user`) and Secret Access Key (`password`)
- **aws_region** — AWS region identifier for the target bucket
- **bucket_name** — name of the S3 bucket
- **local_file** — absolute path to the file on the UAC agent host file system
- **s3_object_key** — destination object key within the S3 bucket

### Execution Flow

**Step 1: Validate required fields**
- Confirm that `aws_credentials`, `aws_region`, `bucket_name`, `local_file`, and `s3_object_key` are all non-empty.
- If any required field is missing or empty, raise `ValidationError` with exit code 20 and a descriptive status message. No file system or S3 API access is attempted.

**Step 2: Check local file existence**
- Verify the path specified in `local_file` exists as a file on the agent host file system.
- If the path does not exist or is not a regular file, raise `LocalFileNotFoundError` with exit code 1 and status description `Error: Local file not found — <local_file>`.
- If the path exists but is not readable due to permissions, raise `LocalFileNotFoundError` with exit code 1 and status description `Error: Local file not found — <local_file>`.

**Step 3: Create S3 client**
- Instantiate a boto3 S3 client using:
  - `aws_credentials["user"]` as the AWS Access Key ID
  - `aws_credentials["password"]` as the AWS Secret Access Key
  - `aws_region` as the `region_name`
- No session token is used.

**Step 4: Upload the file**
- Call boto3 `upload_file(local_file, bucket_name, s3_object_key)`.
- If a boto3 `ClientError` is raised during upload, classify the error code and raise the appropriate custom exception (see Exception Mapping Strategy).

**Step 5: Retrieve ETag**
- Call `head_object(Bucket=bucket_name, Key=s3_object_key)` on the newly uploaded object.
- Extract the `ETag` value from the response.
- Strip any surrounding double-quote characters from the ETag string (AWS returns ETags wrapped in quotes).

**Step 6: Build S3 URI**
- Construct `s3_uri` = `s3://<bucket_name>/<s3_object_key>`.

**Step 7: Print confirmation and populate output**
- Print to STDOUT: `File uploaded successfully to s3://<bucket_name>/<s3_object_key>`
- Set `output_data.status` = `Success: File uploaded to s3://<bucket_name>/<s3_object_key>`
- Set `output_data.s3_uri` = `s3://<bucket_name>/<s3_object_key>`
- Return Extension Output `result` containing:
  - `s3_uri`: the full S3 URI string
  - `etag`: the cleaned ETag string
- Return exit code 0.

### Output Examples

**STDOUT**:
```
File uploaded successfully to s3://my-demo-bucket/reports/2026-01-15.csv
```

**Extension Output result object (JSON)**:

The Extension output also includes `exit_code`, `status_description`, and `invocation` elements added automatically during implementation.

```json
{
  "result": {
    "s3_uri": "s3://my-demo-bucket/reports/2026-01-15.csv",
    "etag": "d41d8cd98f00b204e9800998ecf8427e"
  }
}
```

### Success Criteria

1. The local file exists and is readable on the agent host.
2. The S3 bucket is accessible with the provided credentials and region.
3. The file is successfully uploaded to the specified S3 object key.
4. Return code is 0.
5. Extension Output JSON `result` contains `s3_uri` and `etag`.
6. Output field `status` = `Success: File uploaded to s3://<bucket>/<key>`.
7. Output field `s3_uri` = `s3://<bucket>/<key>`.

---

# Progress Reporting

Progress Reporting (percentage of completion report) is not required.

---

# Dynamic Choice Field Population

No Dynamic choice fields should be implemented.

---

# Cancellation Behavior

Default cancellation logic is used (TERM signal). No custom cancellation code is required. The extension holds no persistent resources requiring explicit cleanup beyond what boto3 manages internally.

---

# Re-Run Behavior

Re-runs are treated as initial executions. Both actions are idempotent: re-running List Objects repeats the listing with fresh results; re-running Upload File overwrites the existing S3 object at the specified key. No output fields from previous runs are used to alter execution logic.

---

# Dynamic Commands

No Dynamic commands should be implemented.

---

# Utility Modules

## Required Utility Modules

### 1. AWS S3 Utility

**Purpose:** Encapsulates all boto3 S3 client creation and S3 API operations used by both actions, centralising error classification into custom exceptions.

**Required Capabilities:**

**S3 Client Creation:**
- Accept `access_key_id` (string), `secret_access_key` (string), and `region_name` (string) as parameters
- Return a configured boto3 S3 client instantiated with these static credentials
- No session token support

**Object Listing (used by List Objects action):**
- Accept `s3_client`, `bucket_name` (string) as parameters
- Paginate through all pages of `list_objects_v2` using `ContinuationToken` until `IsTruncated` is `False`
- On each page, extract `Key`, `Size`, and `LastModified` from the `Contents` list; accumulate across pages
- Track `total_count` as the sum of `KeyCount` per page
- Return a tuple: (full object list as list of dicts with keys `key`, `size_bytes`, `last_modified`; `total_count` as integer)
- Classify `ClientError` exceptions and raise appropriate custom exceptions (see Exception Mapping Strategy)

**File Upload (used by Upload File action):**
- Accept `s3_client`, `local_file` (string), `bucket_name` (string), `s3_object_key` (string) as parameters
- Invoke `upload_file(local_file, bucket_name, s3_object_key)` on the s3_client
- After successful upload, invoke `head_object(Bucket=bucket_name, Key=s3_object_key)` on the s3_client
- Extract the `ETag` from the `head_object` response; strip surrounding double-quote characters
- Return the cleaned ETag string
- Classify `ClientError` exceptions and raise appropriate custom exceptions

**Error Classification:**
- `ClientError` code `InvalidClientTokenId`, `SignatureDoesNotMatch`, `AuthFailure`, or `AccessDenied` → raise `AuthenticationError`
- `ClientError` code `NoSuchBucket` → raise `BucketNotFoundError`
- `ClientError` code `IllegalLocationConstraintException` or `PermanentRedirect` → raise `RegionEndpointError`
- `EndpointResolutionError`, `NoRegionError`, or any DNS/connection failure → raise `RegionEndpointError`
- Any other `ClientError` → raise `S3ApiError` with the original error message preserved

**Used By:** List Objects action, Upload File action

---

### 2. Output Formatter Utility

**Purpose:** Provides formatting helpers for generating human-readable STDOUT output for the List Objects action.

**Required Capabilities:**

**Human-Readable Size Formatting:**
- Accept a byte count (non-negative integer) as input
- Use powers of 1024 for unit thresholds: 1 KB = 1,024 bytes; 1 MB = 1,048,576 bytes; 1 GB = 1,073,741,824 bytes; 1 TB = 1,099,511,627,776 bytes
- Select the largest unit where the converted value is ≥ 1.0
- Format to one decimal place with the unit label appended (e.g., `42.5 KB`, `1.2 GB`, `512.0 B`)
- Return the formatted string

**ASCII Table Rendering:**
- Accept a list of object dicts (each with `key` string, `size_bytes` integer, `last_modified` ISO 8601 UTC string) as input
- For each object, convert `size_bytes` to human-readable format using the size formatter
- Render the list as a table using `tabulate` with `tablefmt="rounded_outline"`
- Column headers: `Object Key`, `Size`, `Last Modified`
- Return the complete rendered table as a string

**Used By:** List Objects action

---

## Exception Mapping Strategy

**AWS Authentication Errors:**
- `ClientError` code `InvalidClientTokenId` → `AuthenticationError` (exit code 1, invalid Access Key ID — user configuration error)
- `ClientError` code `SignatureDoesNotMatch` → `AuthenticationError` (exit code 1, invalid Secret Access Key — user configuration error)
- `ClientError` code `AuthFailure` → `AuthenticationError` (exit code 1, general auth failure — user configuration error)
- `ClientError` code `AccessDenied` → `AuthenticationError` (exit code 1, insufficient IAM permissions — user configuration error)

**AWS Resource / Configuration Errors:**
- `ClientError` code `NoSuchBucket` → `BucketNotFoundError` (exit code 1, bucket does not exist or is inaccessible — user configuration error)
- `ClientError` code `IllegalLocationConstraintException` → `RegionEndpointError` (exit code 1, bucket in a different region than specified — user configuration error)
- `ClientError` code `PermanentRedirect` → `RegionEndpointError` (exit code 1, region mismatch causing redirect — user configuration error)
- `EndpointResolutionError`, `NoRegionError`, DNS/connection failure → `RegionEndpointError` (exit code 1, invalid or unreachable region endpoint — user configuration error)

**File System Errors:**
- `FileNotFoundError` when checking `local_file` → `LocalFileNotFoundError` (exit code 1, file path does not exist — user input error)
- `PermissionError` when checking `local_file` → `LocalFileNotFoundError` (exit code 1, file exists but not readable — user input error)

**Validation Errors:**
- Missing or empty required field value → `ValidationError` (exit code 20, checked before any API call — user input error)

**S3 API Errors:**
- Any other `ClientError` not classified above → `S3ApiError` (exit code 1, unexpected S3 service-side error)

**Exit Code Guide:**
- Exit code 0: Successful execution
- Exit code 1: Execution error — authentication, configuration, file system, or S3 API failure (non-transient)
- Exit code 20: Validation error — missing or invalid required input field (non-transient, user must correct input)

---

# Dependencies

## 1. External API Dependencies

**1. Amazon S3 (Simple Storage Service)**
- **Endpoint**: `https://s3.<aws_region>.amazonaws.com`
- **Purpose**: Object storage API used for listing bucket objects (List Objects action) and uploading files (Upload File action)
- **Protocol**: HTTPS
- **Method**: GET (list_objects_v2 via paginator), PUT (upload_file multipart), HEAD (head_object for ETag retrieval)
- **Authentication**: AWS Signature Version 4, handled automatically by boto3/botocore using the provided Access Key ID and Secret Access Key
- **Response Format**: XML deserialized to Python dicts by boto3/botocore
- **Data Retrieved/Sent**: Object metadata (key, size, last modified) for list; binary file data for upload; ETag string for upload confirmation

**General API Requirements:**
- Requires an AWS account with an IAM user holding at minimum `s3:ListBucket` on the target bucket for List Objects, and `s3:PutObject` + `s3:GetObject` on the target bucket for Upload File.
- No separate API key beyond the IAM credential is needed; the UAC Credential entity provides all authentication material.

---

## 2. Python Version Dependency

Python >= 3.11

---

## 3. Target Platform

Linux (x86_64). C extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules. All specified dependencies (boto3, botocore, s3transfer, tabulate) are pure-Python and cross-platform compatible.

---

## 4. Python Library Dependencies

**1. boto3**
- **Purpose**: AWS SDK for Python — provides the S3 client for all List Objects and Upload File operations
- **Version**: `==1.43.97`
- **Installation**: `pip install boto3==1.43.97`
- **Usage**: AWS S3 Utility module — S3 client creation, `list_objects_v2` pagination, `upload_file`, `head_object`
- **Features Used**: `boto3.client('s3', aws_access_key_id, aws_secret_access_key, region_name)`, `list_objects_v2`, `upload_file`, `head_object`

**2. botocore**
- **Purpose**: Core low-level dependency of boto3 — handles AWS request signing, retries, and transport
- **Version**: `==1.43.97`
- **Installation**: `pip install botocore==1.43.97`
- **Usage**: AWS S3 Utility module — exception classification (`botocore.exceptions.ClientError`, `botocore.exceptions.EndpointResolutionError`)
- **Features Used**: `botocore.exceptions.ClientError`, `botocore.exceptions.EndpointResolutionError`, `botocore.exceptions.NoRegionError`

**3. s3transfer**
- **Purpose**: S3 transfer manager — transparently handles multipart uploads within the boto3 `upload_file` call
- **Version**: `==0.19.2`
- **Installation**: `pip install s3transfer==0.19.2`
- **Usage**: Indirectly invoked by boto3's `upload_file`; no direct import required in extension code
- **Features Used**: Multipart upload orchestration (transparent)

**4. tabulate**
- **Purpose**: ASCII table formatter — renders the List Objects result set as a formatted table in STDOUT
- **Version**: `==0.10.0`
- **Installation**: `pip install tabulate==0.10.0`
- **Usage**: Output Formatter Utility — table rendering with `tablefmt="rounded_outline"`
- **Features Used**: `tabulate(data, headers=[...], tablefmt="rounded_outline")`

---

## 5. Python Standard Library Dependencies

**1. os**
- **Purpose**: Environment variable access
- **Version**: Standard library (Python 3.11+)
- **Installation**: No installation required
- **Usage**: List Objects action — reading `UE_MAX_OUTPUT_RECORDS` via `os.environ.get`
- **Features Used**: `os.environ.get`

**2. pathlib**
- **Purpose**: File existence and type checking for local_file validation
- **Version**: Standard library (Python 3.11+)
- **Installation**: No installation required
- **Usage**: Upload File action — verifying that `local_file` exists and is a regular file before any S3 API call
- **Features Used**: `Path.is_file()`

---

## 6. CLI Tool Dependencies

No Dependencies.

---

## 7. Environment Variables

**UE_MAX_OUTPUT_RECORDS** (integer, optional):
- **Purpose**: Controls the maximum number of S3 objects displayed in STDOUT and included in the Extension Output `objects` array for the List Objects action. Does not limit the number of API calls made — all pages are always fetched to obtain the true total count.
- **Default**: `100`
- **Usage**: Read once at the start of List Objects action execution; applied as the truncation threshold after all pages are collected
- **Examples**: `50`, `200`, `1000`
