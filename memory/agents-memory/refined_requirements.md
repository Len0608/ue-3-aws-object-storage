# Universal Extension Requirements (Refined)

**Extension Name:** AWS Object Storage
**Original Generated:** 2026-09-18
**Refined:** 2026-09-18
**Agent_id:** Not specified in source documents
**Requirements Completeness:** Moderate Detail
**Target Platform:** Linux

---

# Table of Contents

1. [Overview](#overview)
2. [Actions](#actions)
   - 2.1 [Action 1 — List Objects](#action-1--list-objects)
   - 2.2 [Action 2 — Upload File](#action-2--upload-file)
3. [Input Requirements](#input-requirements)
   - 3.1 [Action Selection](#action-selection)
   - 3.2 [Connection Parameters](#connection-parameters)
   - 3.3 [Upload File Parameters](#upload-file-parameters)
4. [Output Requirements](#output-requirements)
   - 4.1 [On Success — List Objects](#on-success--list-objects)
   - 4.2 [On Success — Upload File](#on-success--upload-file)
   - 4.3 [On Error](#on-error)
5. [Authentication Requirements](#authentication-requirements)
6. [Environment Variables](#environment-variables)
7. [Operational Behavior](#operational-behavior)
8. [Implementation Notes](#implementation-notes)
   - 8.1 [Python Compatibility](#python-compatibility)
   - 8.2 [Target Platform](#target-platform)
   - 8.3 [Third-Party Services and Tools](#third-party-services-and-tools)
   - 8.4 [Error Handling](#error-handling)
   - 8.5 [Resource Cleanup](#resource-cleanup)
9. [Requirements Summary](#requirements-summary)
10. [Document Change History](#document-change-history)
11. [References](#references)

---

# Overview

This document defines the requirements for the **AWS Object Storage** Universal Extension for Stonebranch Universal Automation Center (UAC).

**Integration Purpose:** The extension provides an MVP/demo AWS S3 integration that demonstrates two core capabilities — listing objects in a specified S3 bucket and uploading a local file from the UAC agent host to a specified S3 bucket and object key. The goal is to demonstrate that AWS S3 integration can be implemented with Stonebranch, keeping implementation simple and free of advanced features.

---

# Actions

## Action 1 — List Objects

**Functional Requirements:**

1. The action must connect to the specified AWS S3 bucket in the specified AWS region using the provided static credentials.
2. The action must retrieve the list of objects contained in the bucket.
3. The action must cap the number of objects returned at the value of the `UE_MAX_OUTPUT_RECORDS` environment variable (default: 100).
4. When the total number of objects in the bucket exceeds the cap, the action must include a truncation note in STDOUT indicating how many objects exist in total versus how many are displayed, along with a hint to set `UE_MAX_OUTPUT_RECORDS` to retrieve more.
5. The action must display the results as a formatted ASCII table in STDOUT showing: object key, size (human-readable format), and last modified timestamp.
6. The action must return a structured JSON Extension Output containing the bucket name, total object count returned, and per-object metadata (key, size in bytes, last modified timestamp).
7. The action must populate the **Status** output-only field with a short success description including the object count.
8. The action must populate the **Object Count** output-only field with the number of objects returned.

---

## Action 2 — Upload File

**Functional Requirements:**

1. The action must connect to the specified AWS S3 bucket in the specified AWS region using the provided static credentials.
2. The action must upload the specified local file from the UAC agent host file system to the specified S3 object key within the bucket.
3. Upon successful upload, the action must write a human-readable confirmation to STDOUT including the full S3 URI of the uploaded object.
4. The action must return a structured JSON Extension Output containing the S3 URI of the uploaded object and the ETag returned by S3.
5. The action must populate the **Status** output-only field with a short success description including the S3 URI.
6. The action must populate the **S3 URI** output-only field with the destination S3 URI of the uploaded file.

---

# Input Requirements

## Action Selection

- **Action** (choice, required): Selects the operation to perform.
  - Available options: `List Objects`, `Upload File`
  - Default presented option: `List Objects`
  - Applicability: All tasks

---

## Connection Parameters

- **AWS Credentials** (credential, required): A UAC Credential entity providing the AWS Access Key ID and AWS Secret Access Key for authenticating with the S3 API.
  - Example: A UAC credential named `aws-s3-demo` where `user` = `AKIAIOSFODNN7EXAMPLE` and `password` = `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
  - Applicability: All actions
  - Default Value: None

- **AWS Region** (text, required): The AWS region identifier where the target S3 bucket resides.
  - Example: `us-east-1`, `eu-west-1`, `ap-southeast-1`
  - Applicability: All actions
  - Default Value: `us-east-1`

- **Bucket Name** (text, required): The name of the AWS S3 bucket to operate on.
  - Example: `my-demo-bucket`
  - Applicability: All actions
  - Default Value: None

---

## Upload File Parameters

These fields are shown only when the **Action** field is set to `Upload File`.

- **Local File** (text, required): The absolute path of the file on the UAC agent host file system to upload.
  - Example: `/data/reports/2026-01-15.csv`
  - Applicability: Upload File action only
  - Default Value: None

- **S3 Object Key** (text, required): The destination object key (path and filename) within the S3 bucket.
  - Example: `reports/2026-01-15.csv`
  - Applicability: Upload File action only
  - Default Value: None

---

# Output Requirements

## On Success — List Objects

**Return code:** 0

**Status description:** `Success: <N> objects listed`
- Example: `Success: 42 objects listed`

**Output-only fields:**
- **Status** (text): Short success description including the object count. Example: `Success: 42 objects listed`
- **Object Count** (text): The number of objects returned. Example: `42`

**STDOUT output:**
- A formatted ASCII table with three columns: **Object Key**, **Size** (human-readable, e.g., `42.5 KB`, `1.2 GB`), and **Last Modified** (UTC timestamp).
- When the result is truncated by the `UE_MAX_OUTPUT_RECORDS` cap, a note must appear after the table:
  `Showing 100 of 342 objects. Set UE_MAX_OUTPUT_RECORDS to retrieve more.`

**Extension Output (JSON):**
```json
{
  "result": {
    "bucket": "my-demo-bucket",
    "object_count": 42,
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

**Success Criteria:**
1. The S3 bucket is accessible with the provided credentials and region.
2. The object list is retrieved and displayed in the ASCII table format.
3. Return code is 0.
4. Extension Output JSON is populated with bucket, object_count, and objects array.
5. Output-only fields Status and Object Count are populated.

---

## On Success — Upload File

**Return code:** 0

**Status description:** `Success: File uploaded to s3://<bucket>/<object_key>`
- Example: `Success: File uploaded to s3://my-demo-bucket/reports/2026-01-15.csv`

**Output-only fields:**
- **Status** (text): Short success description including the S3 URI. Example: `Success: File uploaded to s3://my-demo-bucket/reports/2026-01-15.csv`
- **S3 URI** (text): The full S3 URI of the uploaded object. Example: `s3://my-demo-bucket/reports/2026-01-15.csv`

**STDOUT output:**
- A single confirmation line: `File uploaded successfully to s3://<bucket>/<object_key>`
- Example: `File uploaded successfully to s3://my-demo-bucket/reports/2026-01-15.csv`

**Extension Output (JSON):**
```json
{
  "result": {
    "s3_uri": "s3://my-demo-bucket/reports/2026-01-15.csv",
    "etag": "d41d8cd98f00b204e9800998ecf8427e"
  }
}
```

**Success Criteria:**
1. The local file exists and is accessible on the agent host.
2. The S3 bucket is accessible with the provided credentials and region.
3. The file is successfully uploaded to the specified S3 object key.
4. Return code is 0.
5. Extension Output JSON is populated with s3_uri and etag.
6. Output-only fields Status and S3 URI are populated.

---

## On Error

**Failure Scenarios:**

- **Authentication Failure**
  - Description: The provided AWS Access Key ID or Secret Access Key is invalid or does not have permission to perform the requested S3 operation.
  - Root causes: Wrong credentials, insufficient IAM permissions.
  - Return code: Non-zero
  - Status description pattern: `Error: Authentication failed — <error message>`

- **Invalid Region or Endpoint Error**
  - Description: The specified AWS region does not match the bucket's actual region, or the region identifier is invalid.
  - Root causes: Incorrect AWS Region field value, bucket created in a different region than specified.
  - Return code: Non-zero
  - Status description pattern: `Error: Region/endpoint error — <error message>`

- **Bucket Not Found**
  - Description: The specified bucket does not exist or is not accessible to the authenticated user.
  - Root causes: Bucket name typo, bucket deleted, insufficient IAM bucket-level permissions.
  - Return code: Non-zero
  - Status description pattern: `Error: Bucket not found — <bucket_name>`

- **Local File Not Found** (Upload File only)
  - Description: The specified local file path does not exist on the agent host.
  - Root causes: Incorrect path, file not yet created, wrong agent host.
  - Return code: Non-zero
  - Status description pattern: `Error: Local file not found — <file_path>`

- **S3 API Error**
  - Description: The S3 API returned an unexpected error during list or upload operation.
  - Root causes: AWS service disruption, throttling, permissions boundary violation.
  - Return code: Non-zero
  - Status description pattern: `Error: S3 API error — <error message>`

**Input Validation:**
- Input fields validation is required. Missing required fields must produce a clear error before any S3 API call is attempted.

---

# Authentication Requirements

The extension supports **static credential authentication only**. Authentication uses an AWS Access Key ID and AWS Secret Access Key provided via a UAC Credential entity. The UAC Credential attributes map as follows:

- `user` attribute → AWS Access Key ID
- `password` attribute → AWS Secret Access Key

Session tokens (STS temporary credentials) and IAM Instance Role (implicit authentication) are not supported.

---

# Environment Variables

- **UE_MAX_OUTPUT_RECORDS** (integer, default: `100`): Controls the maximum number of S3 objects returned and displayed by the List Objects action. When the bucket contains more objects than this limit, output is capped and a truncation note is appended to STDOUT. Operators can increase this value to retrieve more objects without code changes.

---

# Operational Behavior

**Dynamic Choice Fields:**
Not applicable. The extension uses no dynamically populated dropdown fields.

**Cancel Action:**
Not specified. Standard UAC task cancellation behavior applies.

**Re-run Capability:**
Standard UAC re-run behavior applies. Both actions are idempotent with respect to re-runs: re-running List Objects repeats the listing; re-running Upload File overwrites the existing S3 object at the specified key.

**Progress Reporting:**
Not specified. No progress bar is required. STDOUT output from boto3 serves as the primary execution log.

**Dynamic Commands:**
Not applicable. The extension defines no dynamic commands.

---

# Implementation Notes

## Python Compatibility

Targeting compatibility for Python >= 3.11 (as specified in extension metadata).

## Target Platform

Target UAC agent platform: **Linux (x86_64)**. C extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules.

## Third-Party Services and Tools

**AWS S3 (Amazon Simple Storage Service)**
- Short Description: Object storage service used for listing and uploading files.
- Version constraints: None specified; current S3 API.
- Integration approach: Access via boto3 Python SDK using static IAM user credentials.

**boto3**
- Short Description: AWS SDK for Python — provides the S3 client for List Objects and Upload File operations.
- Version: 1.43.97
- Type: Pure Python

**botocore**
- Short Description: Core low-level dependency of boto3 — handles AWS API request signing, retries, and transport.
- Version: 1.43.97
- Type: Pure Python

**s3transfer**
- Short Description: S3 transfer manager (boto3 dependency) — handles multipart uploads transparently within the upload operation.
- Version: 0.19.2
- Type: Pure Python

**tabulate**
- Short Description: ASCII table formatter used to render List Objects results in STDOUT.
- Version: 0.10.0
- Type: Pure Python

## Error Handling

**High-level error categories:**
- Authentication errors (invalid credentials, insufficient permissions)
- Configuration errors (invalid region, bucket not found)
- File system errors (local file not found — Upload File action)
- S3 API errors (unexpected service-side failures)

**Error handling strategy:** All errors must produce a non-zero return code, a descriptive status message in the Status output-only field, and informative STDERR output. Errors must be caught and reported cleanly without exposing raw stack traces to the UAC task log.

**Recovery mechanisms:** None specified. The extension does not implement automatic retries or fallback strategies.

## Resource Cleanup

Not specified. The extension holds no persistent connections or temporary files requiring explicit cleanup beyond what the Python S3 client manages internally.

---

# Requirements Summary

The AWS Object Storage Universal Extension is a minimal MVP/demo integration that provides two AWS S3 operations for UAC:

1. **List Objects** — retrieves and displays up to `UE_MAX_OUTPUT_RECORDS` (default 100) objects from a specified S3 bucket as a formatted ASCII table (key, human-readable size, last modified), and returns structured JSON with per-object metadata.
2. **Upload File** — uploads a local file from the agent host to a specified S3 bucket and object key, confirming success with an S3 URI and returning the ETag in the Extension Output JSON.

Authentication is via static AWS IAM credentials (Access Key ID + Secret Access Key) through a UAC Credential entity. The AWS Region field defaults to `us-east-1`. All boto3 dependencies are bundled with the extension. Two output-only fields provide at-a-glance status in the UAC task list: **Status** (always populated) and either **Object Count** or **S3 URI** depending on the action performed.

---

# Document Change History

- 2026-09-18 08:14 UTC: Initial requirements captured (Moderate Detail)
- 2026-09-18: Comprehensive refinement based on 7 clarification questions and user feedback — covering authentication method, tabulate dependency, List Objects output format and metadata, output record cap behavior, Upload File confirmation format, UAC output-only fields, and AWS Region default value

---

# References

- Original Requirements Document: `memory/requirements.md`
- Original Requirements Q&A Document: `memory/agents-memory/requirements-QnA.md`
