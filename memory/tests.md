# Test Plan

**Extension:** AWS Object Storage (ue-3-aws-object-storage)
**Generated:** 2026-09-18

---

## Test: Test_AWSObjectStorage_ListObjects_IAMStatic_Minimal

**Template:** AWS Object Storage
**Agent:** sb-agent-ubu - AGNT0012
**Input Fields:**
- action: List Objects
- aws_credentials: AWS_key_Secret
- aws_region: us-east-1
- bucket_name: salescommission
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains a formatted ASCII table (rounded_outline borders) listing objects in the salescommission bucket
- Output field `status` = `Success: <N> objects listed`
- Output field `object_count` is populated with a numeric string
- Extension Output JSON `result` contains keys: `bucket`, `object_count`, `total_bucket_count`, `truncated`, `objects`

---

## Test: Test_AWSObjectStorage_UploadFile_IAMStatic_Minimal

**Template:** AWS Object Storage
**Agent:** sb-agent-ubu - AGNT0012
**Input Fields:**
- action: Upload File
- aws_credentials: AWS_key_Secret
- aws_region: us-east-1
- bucket_name: salescommission
- local_file: /tmp/report1.txt
- s3_object_key: report1.txt
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains: `File uploaded successfully to s3://salescommission/report1.txt`
- Output field `status` = `Success: File uploaded to s3://salescommission/report1.txt`
- Output field `s3_uri` = `s3://salescommission/report1.txt`
- Extension Output JSON `result` contains keys: `s3_uri`, `etag`

---
