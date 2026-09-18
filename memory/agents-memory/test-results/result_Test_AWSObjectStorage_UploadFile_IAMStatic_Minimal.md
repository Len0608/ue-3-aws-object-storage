## Test: Test_AWSObjectStorage_UploadFile_IAMStatic_Minimal

**Status**: ✗ Failed

### Output:
```
STDOUT:
[empty]

STDERR:
2026-09-18 08:48:31,599 - extension.py[63] INFO: ue-3-aws-object-storage v1.0.0 started
2026-09-18 08:48:31,599 - extension.py[70] INFO: Action requested: Upload File
2026-09-18 08:48:31,599 - extension.py[76] INFO: Executing action: Upload File
2026-09-18 08:48:31,599 - upload_file.py[43] INFO: Starting upload_file action
2026-09-18 08:48:31,599 - upload_file.py[50] INFO: Validating required fields
2026-09-18 08:48:31,599 - upload_file.py[86] INFO: Checking local file existence: /tmp/report1.txt
2026-09-18 08:48:31,600 - upload_file.py[91] ERROR: Local file does not exist or is not a regular file: /tmp/report1.txt
2026-09-18 08:48:31,600 - extension.py[90] ERROR: Execution error: Local File Not Found: Local file not found — /tmp/report1.txt
2026-09-18 08:48:31,621 - extension_start_result.py[221] ERROR: Error in extension: Local File Not Found: Local file not found — /tmp/report1.txt

EXTENSION OUTPUT:
{
  "exit_code": 1,
  "status_description": "Local File Not Found: Local file not found — /tmp/report1.txt",
  "errors": [{"type": "LocalFileNotFoundError", "message": "Local File Not Found: Local file not found — /tmp/report1.txt", "exit_code": 1}]
}
```

### Notes:
- statusCode: FAILED
- exitCode: 1
- extensionStatus: "Checking local file"
- The source file /tmp/report1.txt does not exist on the remote agent host (sb-agent-ubu - AGNT0012)
- Extension correctly raised LocalFileNotFoundError and exited with code 1
