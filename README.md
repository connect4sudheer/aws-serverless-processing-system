# Serverless Processing & Monitoring System

A production-style serverless data processing and monitoring system built with AWS Lambda, Amazon S3, Amazon SQS, Amazon CloudWatch, Amazon SNS, and IAM.

The system automatically processes customer and order CSV files uploaded to Amazon S3, validates records, stores processing results, handles failed Lambda invocations through an SQS Dead-Letter Queue (DLQ), and provides application and infrastructure monitoring with CloudWatch and SNS-based alerts.

## Architecture

```text
                         User / File Source
                                |
                                v
                         Amazon S3
                    uploads/customers/
                     uploads/orders/
                                |
                         ObjectCreated
                                |
                                v
                         AWS Lambda
                    Serverless Processor
                                |
                  +-------------+-------------+
                  |                           |
               SUCCESS                     FAILURE
                  |                           |
                  v                           v
          Processed Result S3            Lambda Retry
                                              |
                                              v
                                           SQS DLQ
                                              |
                                              v
                                          CloudWatch
                                      +-------+-------+
                                      |               |
                                  Dashboard        Alarms
                                                      |
                                                      v
                                                     SNS
                                                      |
                                                      v
                                                    Email
```

## Problem Statement

Organizations often receive customer and order files that require automated validation and processing.

The system should:

- Automatically process files uploaded to S3.
- Validate customer and order records.
- Separate valid and invalid records.
- Store processing results in S3.
- Handle unexpected Lambda processing failures.
- Retry failed asynchronous Lambda invocations.
- Preserve permanently failed events in an SQS DLQ.
- Provide operational visibility through CloudWatch.
- Monitor application-specific data quality.
- Trigger alerts when important thresholds are exceeded.
- Notify operations through SNS.
- Follow least-privilege IAM principles.

## AWS Services Used

| AWS Service | Purpose |
|---|---|
| Amazon S3 | Input and processed file storage |
| AWS Lambda | Serverless file processing |
| Amazon SQS | Dead-Letter Queue for failed processing events |
| Amazon CloudWatch | Logs, built-in metrics, custom metrics, dashboard and alarms |
| Amazon SNS | Notification delivery for alarms |
| AWS IAM | Access control and least-privilege permissions |

## Data Flow

### 1. File Upload

Customer and order CSV files are uploaded to S3:

```text
uploads/
├── customers/
│   └── customers.csv
└── orders/
    └── orders.csv
```

### 2. S3 Trigger

The S3 `ObjectCreated` event invokes the Lambda function asynchronously.

### 3. File Processing

Lambda:

1. Reads the S3 event.
2. Identifies the file type from the S3 prefix.
3. Reads the CSV file.
4. Validates each record.
5. Calculates processing statistics.
6. Creates a processing result.
7. Stores the result in S3.
8. Publishes application metrics to CloudWatch.

### 4. Successful Processing

Results are stored under:

```text
processed/
├── customers/
│   └── customers-result.json
└── orders/
    └── orders-result.json
```

### 5. Failed Processing

Unexpected/system errors cause the Lambda invocation to fail. The configured asynchronous retry mechanism retries the invocation. If processing continues to fail, the event is sent to the SQS DLQ for later investigation.

## Business Validation vs System Failure

The project intentionally distinguishes between business validation errors and system failures.

### Business validation error

Examples:

```text
Invalid email
Invalid phone
Missing customer ID
Invalid quantity
Invalid order amount
```

These do not fail the Lambda invocation. They are recorded in the processing result.

Example:

```json
{
  "total_records": 5,
  "valid_records": 3,
  "invalid_records": 2,
  "errors": [
    {
      "customer_id": "C004",
      "reason": "Invalid Email"
    }
  ]
}
```

### System failure

Examples:

```text
S3 access denied
S3 object unavailable
Unexpected application exception
Unable to write processing result
Invalid Lambda event
```

These cause the Lambda invocation to fail and participate in the configured retry/DLQ flow.

## Project Structure

```text
serverless-processing-monitoring/
|
├── README.md
├── .gitignore
├── requirements.txt
|
├── src/
│   ├── lambda_function.py
│   ├── config.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── customer_handler.py
│   │   └── order_handler.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── s3_service.py
│   │   └── cloudwatch_service.py
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── customer_validator.py
│   │   └── order_validator.py
│   └── utils/
│       ├── __init__.py
│       ├── event_utils.py
│       └── result_utils.py
|
├── tests/
├── sample-data/
├── docs/
└── screenshots/
```

### Modular Design

The Lambda entry point is intentionally kept small.

```text
lambda_function.py
        |
        +-- event_utils
        |
        +-- customer_handler
        |       |
        |       +-- customer_validator
        |
        +-- order_handler
        |       |
        |       +-- order_validator
        |
        +-- s3_service
        |
        +-- cloudwatch_service
```

This separates event handling, business processing, validation, S3 operations, CloudWatch operations, and result generation.

## CloudWatch Monitoring

The system uses both AWS built-in metrics and custom application metrics.

### Lambda Built-in Metrics

AWS automatically provides:

- `Invocations`
- `Errors`
- `Duration`
- `Throttles`

### Custom Application Metrics

The application publishes:

```text
Namespace: ServerlessProcessing

FilesProcessed
TotalRecords
InvalidRecords
InvalidRecordPercentage
```

The metrics include a `FileType` dimension so customer and order processing can be monitored independently.

### SQS Metrics

CloudWatch automatically provides SQS queue metrics. For the DLQ, the primary operational metric is:

```text
ApproximateNumberOfMessagesVisible
```

This indicates messages waiting in the DLQ for investigation.

## CloudWatch Dashboard

The dashboard provides a centralized view of the system.

### Lambda Health

- Invocations
- Errors
- Duration

### Application Health

- FilesProcessed
- TotalRecords
- InvalidRecords
- InvalidRecordPercentage

### Reliability

- DLQ message count

Monitoring provides visibility into system behavior, while alarms identify conditions that require action.

## CloudWatch Alarms

The project includes alarms for conditions that require operational attention.

| Alarm | Metric | Purpose |
|---|---|---|
| Lambda Errors | `Errors` | Detect Lambda execution failures |
| Lambda Duration | `Duration` | Detect unusually slow processing |
| Data Quality | `InvalidRecordPercentage` | Detect high invalid-record percentage |
| DLQ | `ApproximateNumberOfMessagesVisible` | Detect unresolved failed events |

Example:

```text
InvalidRecordPercentage > threshold
                |
                v
          CloudWatch Alarm
                |
                v
               SNS
                |
                v
             Email
```

Not every monitored metric requires an alarm. Metrics such as total records and files processed are primarily useful for visibility and trend analysis.

## SNS Notifications

CloudWatch alarms publish notifications to an SNS topic:

```text
CloudWatch Alarm
       |
       v
   SNS Topic
       |
       v
Email Subscription
```

This provides operational notification when a configured alarm enters the `ALARM` state.

## IAM Permissions

The Lambda execution role requires only the permissions needed by the application.

Typical permissions include:

```text
s3:GetObject
s3:PutObject
cloudwatch:PutMetricData
```

The DLQ configuration also requires the appropriate AWS permissions for the configured failure destination.

AWS access keys and secrets are not stored in the source code.

## Testing Scenarios

### Test 1 — Successful Processing

```text
S3 upload
   |
   v
Lambda
   |
   v
Validation
   |
   v
Processed JSON
```

Expected:

- Lambda succeeds.
- Processing result is stored in S3.
- Custom CloudWatch metrics are published.
- Error alarm remains OK.
- DLQ remains empty.

### Test 2 — Invalid Business Records

A CSV containing invalid records is uploaded.

Expected:

- Lambda completes successfully.
- Invalid records are counted.
- Validation errors are included in the result JSON.
- `InvalidRecordPercentage` increases.
- Data-quality alarm can enter `ALARM` when the threshold is exceeded.

### Test 3 — Lambda/System Failure

A controlled application exception is introduced.

Expected flow:

```text
Lambda failure
     |
     v
Retry
     |
     v
Retry exhausted
     |
     v
SQS DLQ
```

Expected:

- Lambda error metric increases.
- Lambda error alarm can trigger.
- Failed event appears in the DLQ.
- DLQ alarm can trigger.
- SNS notification is generated.

### Test 4 — Performance Monitoring

A controlled delay is introduced to increase Lambda execution duration.

Expected:

- Duration metric increases.
- Duration alarm can enter `ALARM`.
- SNS notification is generated.

## Sample Data

The repository contains sample CSV files for successful and validation-failure scenarios:

```text
sample-data/
├── customers-valid.csv
├── customers-invalid.csv
├── orders-valid.csv
└── orders-invalid.csv
```

## Key Design Decisions

### Why Lambda?

The workload is event-driven and does not require continuously running servers.

### Why S3?

S3 provides durable and scalable object storage for input and processing results.

### Why SQS DLQ?

The requirement is to handle failed processing events rather than queue every uploaded file for normal processing.

S3 directly triggers Lambda for normal processing. SQS is used as the failure destination for events that could not be successfully processed after retries.

### Why custom CloudWatch metrics?

AWS provides infrastructure-level metrics, but it does not know application-specific information such as:

- Number of records processed
- Number of invalid records
- Invalid-record percentage
- Number of files successfully processed

The application therefore publishes these metrics directly to CloudWatch.

### Why separate monitoring and alarms?

Monitoring provides visibility into system behavior.

Alarms identify conditions that require action.

```text
Monitoring
    |
    v
Dashboard
    |
    v
Human visibility

Alarm
    |
    v
Threshold exceeded
    |
    v
SNS notification
```

## Technologies

```text
Python
AWS Lambda
Amazon S3
Amazon SQS
Amazon CloudWatch
Amazon SNS
AWS IAM
CSV
JSON
Boto3
```

## Future Improvements

Potential next iterations include:

- Infrastructure as Code using Terraform or AWS SAM
- Automated deployment through CI/CD
- Automated pytest test execution
- Structured JSON logging
- AWS X-Ray tracing
- Idempotency handling
- Better result versioning/job IDs
- Additional data validation rules
- Centralized configuration
- Improved alert routing

## Learning Outcomes

This project provided hands-on experience with:

- Event-driven serverless architecture
- AWS Lambda
- S3 event notifications
- Asynchronous Lambda invocation
- Lambda retries
- SQS Dead-Letter Queues
- IAM permissions
- CloudWatch built-in metrics
- Custom CloudWatch metrics
- CloudWatch dimensions
- CloudWatch dashboards
- CloudWatch alarms
- SNS notifications
- Python modular architecture
- Exception handling
- Business validation
- End-to-end AWS testing


## Disclaimer
This project was created as a hands-on AWS learning and portfolio project. AWS resources, thresholds, and configurations should be reviewed and hardened according to the requirements of a production environment.
