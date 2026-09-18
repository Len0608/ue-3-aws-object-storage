# UAC Entities

**Extension:** AWS Object Storage (ue-3-aws-object-storage)

---

## Agent Selection

### Available Agents

| Agent Name | Host | IP | Type | Status | Queue | Version |
|------------|------|----|------|--------|-------|---------|
| AGT_LINUX_PS5 | ip-30-0-1-83 | 30.0.1.83 | Linux/Unix | Offline | AGNT0071 | 7.7.1.1 |
| nginx-with-sidecar - AKS-SIDECAR-TEST | nginx-with-sidecar | 10.244.4.224 | Linux/Unix | Active | AKS-SIDECAR-TEST | 7.9.2.2 |
| sb-agent-ubu - AGNT0012 | sb-agent-ubu | 127.0.1.1 | Linux/Unix | Active | AGNT0012 | 7.9.0.0 |
| UDMG-SB | ip-172-31-2-26.us-east-2.compute.internal | 172.31.2.26 | Linux/Unix | Active | AGNT0118 | 7.9.2.0 |

### Selected Agent

| Field      | Value |
|------------|-------|
| Agent Name | sb-agent-ubu - AGNT0012 |
| Host Name  | sb-agent-ubu |
| IP Address | 127.0.1.1 |
| Type       | Linux/Unix |
| Status     | Active |
| Queue Name | AGNT0012 |
| Version    | 7.9.0.0 |
| SysID      | 360fb3ad9d0e41cb8530848d37831fe9 |

**Required OS Type:** Linux
**Selection rationale:** First active Linux agent with the `aws-object-storage` extension already installed, making it the most suitable host for running AWS S3 operations.

---

## Required Entities

### Credentials

| Credential Name | Type | Field Name | Auth Method | Used In Scenarios |
|----------------|------|------------|-------------|-------------------|
| AWS_key_Secret | Credential | aws_credentials | IAM Static (Access Key ID + Secret Access Key) | Test_AWSObjectStorage_ListObjects_IAMStatic_Minimal, Test_AWSObjectStorage_UploadFile_IAMStatic_Minimal |

### Scripts

_No script entities required for this extension._

---

## Created Entities

[Populated by main thread after creation on UAC]

### Credentials

| Credential Name | SysID | Status |
|----------------|-------|--------|

### Scripts

| Script Name | SysID | Status |
|------------|-------|--------|
