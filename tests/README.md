# Tests

This directory contains lightweight automated tests for the Python business-validation logic.

The project is primarily a DevOps/AWS serverless project, so the tests focus on application validation logic rather than trying to unit-test AWS itself.

## Test Coverage

### Customer validation
- Valid customer
- Missing customer ID
- Invalid email
- Invalid phone number
- Missing name

### Order validation
- Valid order
- Missing order ID
- Invalid quantity
- Invalid amount
- Missing customer ID

## Run the tests

From the project root:

```bash
pytest tests/
```

The AWS integration was validated separately through end-to-end testing of:

```text
S3 → Lambda → S3
          ↓
       CloudWatch
          ↓
        Alarms
          ↓
         SNS
          ↓
        Email
```

The tests in this directory are intentionally lightweight and complement the AWS integration tests.
