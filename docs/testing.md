# Testing

## Testing Strategy

Testing for this project is divided into two areas:

1. Lightweight automated tests for Python business-validation logic.
2. End-to-end testing of the AWS serverless architecture.

The project is primarily an AWS/DevOps project, so the AWS integration is validated through actual AWS resources rather than attempting to unit-test AWS itself.

---

## Test 1 — Valid Customer File

### Input

A valid customer CSV is uploaded to:

```text
uploads/customers/
```

### Expected

```text
S3
 |
 v
Lambda
 |
 v
Customer validation
 |
 v
Processed JSON
```

Expected results:

- Lambda invocation succeeds.
- Processing result is written to S3.
- Custom CloudWatch metrics are published.
- Lambda Errors remains zero for the successful invocation.
- No event is sent to the DLQ.

### Result

PASS

---

## Test 2 — Invalid Customer Records

A customer CSV containing invalid values is uploaded.

Example:

```text
Total records = 5
Invalid records = 2
Invalid record percentage = 40%
```

### Expected

- Lambda completes successfully.
- Invalid records are counted.
- Validation reasons are stored in the result JSON.
- `InvalidRecordPercentage` is published to CloudWatch.
- The data-quality alarm enters `ALARM` when the configured threshold is exceeded.

### Result

PASS

---

## Test 3 — Valid Order File

A valid order CSV is uploaded to:

```text
uploads/orders/
```

### Expected

- Lambda identifies the file as an order file.
- Order validation executes.
- Processing result is written to the order processed prefix.
- Order-specific CloudWatch metrics are published.

### Result

PASS

---

## Test 4 — Lambda Failure and Retry

A controlled exception is introduced into the Lambda processing path.

### Expected Flow

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

### Expected

- Lambda Errors metric increases.
- Lambda retries the failed asynchronous invocation.
- Failed event is eventually sent to the DLQ.
- Failed event can be inspected in SQS.

### Result

PASS

---

## Test 5 — Lambda Error Alarm

The Lambda Error alarm monitors the AWS/Lambda `Errors` metric.

### Condition

```text
Errors >= 1
```

### Expected

```text
Lambda error
     |
     v
CloudWatch Errors metric
     |
     v
Alarm enters ALARM
     |
     v
SNS notification
```

### Result

PASS

---

## Test 6 — Duration Alarm

A controlled delay is introduced to increase Lambda execution duration.

### Expected

- Lambda Duration metric increases.
- Duration alarm detects the configured threshold breach.
- SNS notification is generated.

### Result

PASS

---

## Test 7 — Invalid Record Percentage Alarm

A file containing a high percentage of invalid records is uploaded.

### Expected

```text
InvalidRecordPercentage > configured threshold
                  |
                  v
            CloudWatch Alarm
                  |
                  v
                 SNS
```

### Result

PASS

---

## Test 8 — DLQ Alarm

A failed event is allowed to reach the DLQ.

The alarm monitors:

```text
ApproximateNumberOfMessagesVisible
```

### Expected

```text
DLQ message count > 0
          |
          v
CloudWatch Alarm
          |
          v
SNS notification
```

### Result

PASS

---

## Test 9 — SNS Notification

A CloudWatch alarm is triggered intentionally.

### Expected

```text
CloudWatch Alarm
       |
       v
SNS Topic
       |
       v
Confirmed Email Subscription
       |
       v
Email Notification
```

### Result

PASS

---

## Automated Python Tests

The repository also contains lightweight pytest tests for business validation.

```text
tests/
├── README.md
├── test_customer_validator.py
└── test_order_validator.py
```

These cover scenarios such as:

- Valid customer
- Missing customer ID
- Invalid email
- Invalid phone
- Missing name
- Valid order
- Missing order ID
- Invalid quantity
- Invalid amount
- Missing customer ID

Run them from the project root with:

```bash
pytest tests/
```

---

## Test Philosophy

The objective is not to create a large test suite for AWS services.

Instead:

```text
Python business logic
        |
        v
Automated unit tests

AWS architecture
        |
        v
End-to-end integration tests
```

This provides coverage of both the application logic and the actual AWS serverless workflow.
