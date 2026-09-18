## Test: Test_AWSObjectStorage_ListObjects_IAMStatic_Minimal

**Status**: ✓ Success

### Output:
```
STDOUT:
╭───────────────────────────────────────────────┬─────────┬──────────────────────╮
│ Object Key                                    │ Size    │ Last Modified        │
├───────────────────────────────────────────────┼─────────┼──────────────────────┤
│ /                                             │ 0.0 B   │ 2024-02-01T13:56:49Z │
│ report1.txt                                   │ 67.0 B  │ 2026-09-17T10:01:43Z │
│ reports/                                      │ 0.0 B   │ 2024-08-06T10:37:49Z │
│ reports/2026/q3/report1.txt                   │ 62.0 B  │ 2026-09-14T08:19:25Z │
│ reports/report1.txt                           │ 78.4 KB │ 2024-08-06T10:39:00Z │
│ sales/                                        │ 0.0 B   │ 2026-02-02T17:35:44Z │
│ sales/culinax_sales_01_2026.csv               │ 908.0 B │ 2026-02-18T17:18:05Z │
│ sales/sales_2026_March.csv                    │ 104.0 B │ 2026-03-16T09:30:51Z │
│ sellerdata/                                   │ 0.0 B   │ 2026-03-16T09:49:33Z │
│ sellerdata/culinax_sentiment_data_01_2026.csv │ 2.9 KB  │ 2026-05-04T18:37:43Z │
│ sentiment/                                    │ 0.0 B   │ 2026-02-18T17:26:03Z │
│ sentiment/culinax_sentiment_data_01_2026.csv  │ 2.9 KB  │ 2026-06-24T16:27:21Z │
│ test/report1.txt                              │ 62.0 B  │ 2026-09-14T09:01:36Z │
│ uploads/full-test/report1.txt                 │ 62.0 B  │ 2026-09-14T08:19:27Z │
│ userverse.txt                                 │ 70.0 B  │ 2026-09-17T14:00:52Z │
╰───────────────────────────────────────────────┴─────────┴──────────────────────╯

EXTENSION OUTPUT:
{
  "exit_code": 0,
  "status_description": "Successful Execution",
  "metadata": {"version": "1.0.0", "extension": "ue-3-aws-object-storage"},
  "result": {
    "bucket": "salescommission",
    "object_count": 15,
    "total_bucket_count": 15,
    "truncated": false
  },
  "errors": []
}
```

### Notes:
- extensionStatus: "Success: 15 objects listed"
- statusCode: SUCCESS
- exitCode: 0
- 15 objects returned from bucket "salescommission" via IAM static credentials
