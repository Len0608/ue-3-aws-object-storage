# Test Environment Setup Guide

**Extension:** AWS Object Storage (ue-3-aws-object-storage)  
**Generated:** 2026-09-18  
**Test Scenarios:** 2 total

---

## 🌐 EXTERNAL SERVICE SETUP: AWS S3

BEFORE RUNNING TESTS, CREATE AND VERIFY THE FOLLOWING ON AWS:

### 1. S3 Bucket: `salescommission`

**What:** An AWS S3 bucket named exactly `salescommission`.

**Why:** Both test scenarios operate on this bucket — one lists objects within it, the other uploads a file to it. The bucket must exist and be accessible with the provided AWS credentials.

**How:**

1. Log in to the AWS Management Console.
2. Navigate to the **S3 service**.
3. Click **Create bucket**.
4. Enter bucket name: `salescommission`
5. Select the region where you want to create the bucket. The test will specify a region (default: `us-east-1`). Ensure you select the same region or update the test parameters to match your bucket's region.
6. Accept default settings and click **Create bucket**.
7. Verify the bucket appears in your bucket list.

**Example:**
- Bucket name: `salescommission`
- Region: `us-east-1` (or any region you choose — must match test parameters)
- Versioning: Disabled (default)
- Public access: Blocked (default)

---

### 2. IAM Permissions for AWS Credentials

**What:** The AWS credentials (Access Key ID and Secret Access Key) supplied via the `AWS_key_Secret` UAC Credential must have permissions to list objects in the bucket and upload files to it.

**Why:** The extension's List Objects action requires `s3:ListBucket` permission. The Upload File action requires `s3:PutObject` and `s3:GetObject` permissions. Without these permissions, the tests will fail with authentication or authorization errors.

**How:**

1. Log in to the AWS Management Console.
2. Navigate to the **IAM service**.
3. Find the IAM user associated with the Access Key ID in the `AWS_key_Secret` credential.
4. Attach or verify an inline policy (or managed policy) that grants the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucketContents",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::salescommission"
    },
    {
      "Sid": "UploadAndRetrieve",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::salescommission/*"
    }
  ]
}
```

5. If attaching a new inline policy, click **Add inline policy**, paste the JSON above, and save.
6. If using a managed policy, search for and attach a policy that includes `s3:ListBucket`, `s3:PutObject`, and `s3:GetObject` on the `salescommission` bucket.

**Example Verification:**
- User: `len` (from environment.md)
- Bucket: `arn:aws:s3:::salescommission`
- Required actions: `s3:ListBucket` (list objects), `s3:PutObject` (upload), `s3:GetObject` (retrieve ETag)

---

## 🖥️ AGENT HOST SETUP

BEFORE RUNNING TESTS, PREPARE THE FOLLOWING ON THE UAC AGENT MACHINE:

### 1. Test Input File: `/tmp/report1.txt`

**What:** A plain-text file at the absolute path `/tmp/report1.txt` on the UAC Agent host.

**Why:** The second test scenario (Upload File) requires this file to exist and be readable. The extension will upload this file to the S3 bucket with the object key `report1.txt`. If the file does not exist or is not readable, the upload test will fail with error code 1.

**How:**

Create the file using one of the following methods:

**Option A: Using shell commands (quickest)**
```bash
mkdir -p /tmp
echo "Sales Commission Report - 2026-01-15" > /tmp/report1.txt
chmod 644 /tmp/report1.txt
```

**Option B: Create manually**
1. SSH or log in to the UAC Agent host.
2. Open a text editor: `nano /tmp/report1.txt` or `vi /tmp/report1.txt`
3. Add any content (e.g., "Sales Commission Report - 2026-01-15").
4. Save and close the editor.
5. Verify permissions: `ls -la /tmp/report1.txt` — output should show `-rw-r--r--` or similar (world-readable).

**Example File Content:**
```
Sales Commission Report - 2026-01-15
Generated: 2026-01-15T08:22:10Z
Records: 42
Total Amount: $125,432.00
```

**Verification:**
```bash
# Verify file exists and is readable
test -f /tmp/report1.txt && test -r /tmp/report1.txt && echo "File is readable" || echo "File not found or not readable"

# Check file size
ls -lh /tmp/report1.txt
```

---

## 📋 CHECKLIST

Complete the following before running tests:

**External Service (AWS):**
- ☐ S3 bucket `salescommission` created in the region specified in test parameters (default: `us-east-1`)
- ☐ IAM user (Access Key ID: from `AWS_key_Secret` credential) has `s3:ListBucket` permission on `salescommission`
- ☐ IAM user has `s3:PutObject` and `s3:GetObject` permissions on `salescommission/*`
- ☐ Verified: AWS credentials (Access Key ID and Secret Access Key) are valid and accessible

**Agent Host:**
- ☐ File `/tmp/report1.txt` exists on the UAC Agent machine
- ☐ File is readable by the UAC agent process (typically runs as a system user or service account)
- ☐ Verified: `ls -la /tmp/report1.txt` shows the file with read permissions

**Region Alignment:**
- ☐ If using a region other than `us-east-1`, note the region name and ensure test parameters specify the correct AWS region in the task JSON

---

## Test Scenario Mapping

The following test scenarios will be executed:

| # | Test Scenario | Requires | 
|---|---|---|
| 1 | List objects in AWS S3 Bucket "salescommission" | S3 bucket `salescommission` + valid AWS credentials |
| 2 | Copy a file from /tmp/report1.txt to AWS S3 Bucket "salescommission" | Test file `/tmp/report1.txt` + S3 bucket + valid AWS credentials |

---

## Troubleshooting

**Test 1 Fails: List Objects**
- *Error: `NoSuchBucket`* → Verify bucket `salescommission` exists in the specified region and is accessible with the provided AWS credentials.
- *Error: `InvalidClientTokenId` or `SignatureDoesNotMatch`* → Verify Access Key ID and Secret Access Key are correct in the `AWS_key_Secret` credential.
- *Error: `AccessDenied`* → Verify the IAM user has `s3:ListBucket` permission on the bucket.

**Test 2 Fails: Upload File**
- *Error: `Error: Local file not found — /tmp/report1.txt`* → Create the file using the instructions above and verify it exists: `ls -l /tmp/report1.txt`.
- *Error: `NoSuchBucket`* → Verify bucket `salescommission` exists in the specified region.
- *Error: `InvalidClientTokenId` or `SignatureDoesNotMatch`* → Verify AWS credentials in the `AWS_key_Secret` credential.
- *Error: `AccessDenied`* → Verify the IAM user has `s3:PutObject` and `s3:GetObject` permissions.

---

*This document was generated for test phase preparation. Refer to `memory/analysis.md` for detailed action specifications and field definitions.*
