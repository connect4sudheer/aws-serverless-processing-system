# AWS Services

## Amazon S3

### Purpose

S3 is the entry point and storage layer for the application.

It is used for:

- Receiving customer CSV files
- Receiving order CSV files
- Storing processed JSON results

### Folder Structure

```text
uploads/
├── customers/
└── orders/

processed/
├── customers/
└── orders/
```

### Why S3?

The workload is file-based and event-driven. S3 provides durable object storage and can automatically generate events when objects are created.

---

## AWS Lambda

### Purpose

Lambda performs the serverless processing of uploaded CSV files.

Responsibilities include:

- Reading S3 events
- Reading CSV files
- Validating records
- Generating processing results
- Writing results to S3
- Publishing custom CloudWatch metrics

### Why Lambda?

The application does not require continuously running servers. Processing happens when a file is uploaded, making Lambda a natural event-driven compute service.

---

## Amazon SQS

### Purpose

SQS is used as the Dead-Letter Queue for failed asynchronous Lambda invocations.

It is not used as the primary processing queue.

### Why?

The current workload does not require normal uploads to be queued before processing.

The desired flow is:

```text
S3 -> Lambda
```

while failures follow:

```text
Lambda failure
     |
     v
Retry
     |
     v
SQS DLQ
```

The DLQ preserves failed events for later investigation.

---

## Amazon CloudWatch

### Purpose

CloudWatch provides:

- Lambda logs
- AWS service metrics
- Custom application metrics
- Dashboards
- Alarms

### Built-in Metrics

Examples:

```text
Lambda:
- Invocations
- Errors
- Duration
- Throttles

SQS:
- ApproximateNumberOfMessagesVisible
- NumberOfMessagesSent
- NumberOfMessagesDeleted
```

### Custom Metrics

The application publishes:

```text
Namespace: ServerlessProcessing

FilesProcessed
TotalRecords
InvalidRecords
InvalidRecordPercentage
```

The `FileType` dimension separates customer and order processing.

---

## Amazon SNS

### Purpose

SNS is used as the notification layer for CloudWatch alarms.

Flow:

```text
CloudWatch Alarm
       |
       v
SNS Topic
       |
       v
Email Subscription
```

This allows operational users to receive notifications when an important threshold is exceeded.

---

## AWS IAM

### Purpose

IAM controls access between Lambda and other AWS services.

Typical Lambda permissions include:

```text
s3:GetObject
s3:PutObject
cloudwatch:PutMetricData
```

The project follows the least-privilege principle by granting only the permissions required for the application's operations.

AWS credentials are not stored in the source code.

---

## Service Interaction Summary

| Service | Role |
|---|---|
| S3 | Input and output storage |
| Lambda | Serverless processing |
| SQS | Failed-event/DLQ handling |
| CloudWatch | Logs, metrics, dashboards and alarms |
| SNS | Notifications |
| IAM | Access control |
