# config.py

# CloudWatch namespace used by our application-specific metrics.
CLOUDWATCH_NAMESPACE = "ServerlessProcessing"


# S3 prefixes used to identify the type of uploaded file.
CUSTOMER_UPLOAD_PREFIX = "uploads/customers/"
ORDER_UPLOAD_PREFIX = "uploads/orders/"


# S3 prefixes where processing results will be stored.
CUSTOMER_OUTPUT_PREFIX = "processed/customers/"
ORDER_OUTPUT_PREFIX = "processed/orders/"


# Supported file types.
CUSTOMER_FILE_TYPE = "customer"
ORDER_FILE_TYPE = "order"