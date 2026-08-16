# Architecture

## Overview

This project implements an event-driven serverless processing and monitoring system for customer and order CSV files.

The system uses Amazon S3 as the file entry point, AWS Lambda for processing, Amazon SQS as a Dead-Letter Queue for failed asynchronous invocations, Amazon CloudWatch for monitoring and alarms, and Amazon SNS for operational notifications.

## High-Level Architecture

```text
                         S3
                          |
                    ObjectCreated
                          |
                          v
                       Lambda
                          |
              +-----------+-----------+
              |                       |
           Success                  Failure
              |                       |
              v                       v
       Processed S3              Lambda Retry
                                      |
                                      v
                                    SQS DLQ
                                      |
                                      v
                                 CloudWatch
                                /          \
                           Dashboard       Alarm
                                             |
                                             v
                                            SNS
                                             |
                                             v
                                           Email
```

## Normal Processing Flow

1. A CSV file is uploaded to the appropriate S3 upload prefix.
2. S3 generates an `ObjectCreated` event.
3. The event asynchronously invokes Lambda.
4. Lambda extracts the bucket and object key.
5. The application identifies whether the file is for customers or orders.
6. The CSV is read from S3.
7. Each record is validated.
8. Valid and invalid record counts are calculated.
9. A JSON processing result is written to the processed S3 prefix.
10. Application metrics are published to CloudWatch.

## Business Validation

Business validation failures do not fail the Lambda invocation.

Examples include:

- Missing customer ID
- Invalid email
- Invalid phone number
- Missing order ID
- Invalid quantity
- Invalid amount

These are recorded in the processing result.

```text
CSV
 |
 v
Validate records
 |
 +-- Valid records ------> valid_records
 |
 +-- Invalid records ----> invalid_records + error details
```

## System Failure Flow

System or unexpected application errors are treated differently from business validation errors.

Examples:

- S3 access failure
- Invalid Lambda event
- Unexpected application exception
- Failure while writing the processing result

These cause the Lambda invocation to fail.

```text
Lambda failure
      |
      v
Asynchronous retry
      |
      v
Retry exhausted
      |
      v
SQS Dead-Letter Queue
```

The DLQ preserves the failed event so it can be investigated later.

## Why SQS Is Used as a DLQ

SQS is not used as the normal processing queue in this project.

The normal path is:

```text
S3 -> Lambda
```

The requirement is to process a relatively small number of uploaded files directly.

SQS is used specifically as a failure destination:

```text
S3 -> Lambda -> failure -> retry -> DLQ
```

This avoids introducing unnecessary queueing into the normal processing path while still providing a reliable place to preserve failed events.

## Monitoring Architecture

CloudWatch receives both AWS service metrics and application-specific metrics.

### Built-in metrics

Lambda provides metrics such as:

- Invocations
- Errors
- Duration
- Throttles

SQS provides queue metrics such as:

- ApproximateNumberOfMessagesVisible
- NumberOfMessagesSent
- NumberOfMessagesDeleted

### Custom application metrics

The application publishes:

- FilesProcessed
- TotalRecords
- InvalidRecords
- InvalidRecordPercentage

These metrics use the `FileType` dimension to distinguish customer and order processing.

## Alerting Flow

Selected metrics have CloudWatch alarms.

```text
Metric
  |
  v
CloudWatch Alarm
  |
  | threshold exceeded
  v
SNS Topic
  |
  v
Email Notification
```

Current alarm categories:

- Lambda errors
- Lambda duration
- Invalid record percentage
- DLQ messages

## Python Module Architecture

The application code is separated by responsibility:

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

This keeps the Lambda entry point focused on orchestration rather than mixing business logic, AWS service calls, and validation logic.

## Reliability Considerations

The design separates:

- Business validation failures
- Infrastructure/system failures
- Monitoring and alerting

This allows invalid business data to be reported without unnecessarily retrying the entire file, while genuine processing failures can use Lambda retries and the DLQ.
