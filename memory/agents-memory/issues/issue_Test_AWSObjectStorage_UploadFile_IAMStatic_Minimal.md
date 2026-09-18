## Issue: Test_AWSObjectStorage_UploadFile_IAMStatic_Minimal

**Status**: ✗ Failed

### Expected:
Copy a file from /tmp/report1.txt to AWS S3 Bucket "salescommission" — upload should succeed.

### STDOUT:
[empty]

### STDERR:
2026-09-18 08:48:31,599 - 136927432922816 AsyEvent[EXTENSION_START] - extension.py[63] INFO: ue-3-aws-object-storage v1.0.0 started
2026-09-18 08:48:31,599 - 136927432922816 AsyEvent[EXTENSION_START] - extension.py[70] INFO: Action requested: Upload File
2026-09-18 08:48:31,599 - 136927432922816 AsyEvent[EXTENSION_START] - extension.py[76] INFO: Executing action: Upload File
2026-09-18 08:48:31,599 - 136927432922816 AsyEvent[EXTENSION_START] - upload_file.py[43] INFO: Starting upload_file action
2026-09-18 08:48:31,599 - 136927432922816 AsyEvent[EXTENSION_START] - upload_file.py[50] INFO: Validating required fields
2026-09-18 08:48:31,599 - 136927432922816 AsyEvent[EXTENSION_START] - upload_file.py[86] INFO: Checking local file existence: /tmp/report1.txt
2026-09-18 08:48:31,600 - 136927432922816 AsyEvent[EXTENSION_START] - upload_file.py[91] ERROR: Local file does not exist or is not a regular file: /tmp/report1.txt
2026-09-18 08:48:31,600 - 136927432922816 AsyEvent[EXTENSION_START] - extension.py[90] ERROR: Execution error: Local File Not Found: Local file not found — /tmp/report1.txt
2026-09-18 08:48:31,621 - 136927432922816 AsyEvent[EXTENSION_START] - extension_start_result.py[221] ERROR: Error in extension: /var/opt/universal/uag/extensions/.ue-3-aws-object-storage/extension.py:187 - Local File Not Found: Local file not found — /tmp/report1.txt

### Extension Output:
{
  "exit_code": 1,
  "status_description": "Local File Not Found: Local file not found — /tmp/report1.txt",
  "metadata": {
    "version": "1.0.0",
    "extension": "ue-3-aws-object-storage"
  },
  "input_fields": {
    "action": ["Upload File"],
    "aws_credentials": {"user": "AKIARYOBJ5GY2FWR7V7Y", "password": "****", "token": "", "passphrase": ""},
    "aws_region": "us-east-1",
    "bucket_name": "salescommission",
    "local_file": "/tmp/report1.txt",
    "s3_object_key": "report1.txt"
  },
  "result": {},
  "errors": [
    {
      "type": "LocalFileNotFoundError",
      "message": "Local File Not Found: Local file not found — /tmp/report1.txt",
      "exit_code": 1
    }
  ]
}
