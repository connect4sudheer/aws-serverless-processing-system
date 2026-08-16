# lambda_function.py

import json

from config import (
    CUSTOMER_FILE_TYPE,
    ORDER_FILE_TYPE,
    CUSTOMER_OUTPUT_PREFIX,
    ORDER_OUTPUT_PREFIX,
)

from handlers.customer_handler import process_customer_data
from handlers.order_handler import process_order_data

from services.s3_service import save_json
from services.cloudwatch_service import publish_processing_metrics

from utils.event_utils import (
    extract_s3_event,
    identify_file_type,
)


def lambda_handler(event, context):
    """
    Main AWS Lambda entry point.

    This function is intentionally kept small.

    Its responsibility is to orchestrate the workflow:

        S3 event
            ↓
        Identify file
            ↓
        Process data
            ↓
        Save result
            ↓
        Publish metrics
    """

    try:

        # -------------------------------------------------
        # 1. Extract S3 information from Lambda event
        # -------------------------------------------------

        bucket_name, object_key = extract_s3_event(
            event
        )

        print(
            f"Processing started: "
            f"s3://{bucket_name}/{object_key}"
        )

        # -------------------------------------------------
        # 2. Identify whether this is a customer or
        #    order file.
        # -------------------------------------------------

        file_type = identify_file_type(
            object_key
        )

        print(
            f"Identified file type: {file_type}"
        )

        # -------------------------------------------------
        # 3. Process the file.
        # -------------------------------------------------

        if file_type == CUSTOMER_FILE_TYPE:

            result = process_customer_data(
                bucket_name,
                object_key,
            )

            output_key = (
                f"{CUSTOMER_OUTPUT_PREFIX}"
                f"{object_key.split('/')[-1].replace('.csv', '')}"
                "-result.json"
            )

        elif file_type == ORDER_FILE_TYPE:

            result = process_order_data(
                bucket_name,
                object_key,
            )

            output_key = (
                f"{ORDER_OUTPUT_PREFIX}"
                f"{object_key.split('/')[-1].replace('.csv', '')}"
                "-result.json"
            )

        else:

            raise ValueError(
                f"Unsupported file type: {file_type}"
            )

        # -------------------------------------------------
        # 4. Save processing result to S3.
        # -------------------------------------------------

        save_json(
            bucket_name,
            output_key,
            result,
        )

        # -------------------------------------------------
        # 5. Publish CloudWatch application metrics.
        # -------------------------------------------------

        publish_processing_metrics(
            result,
            file_type,
        )

        print(
            f"Processing completed successfully: "
            f"{object_key}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }

    except ValueError as exc:

        # These are expected validation/configuration
        # problems such as an invalid S3 event or
        # unsupported file location.
        print(
            f"Validation error: {exc}"
        )

        raise

    except Exception as exc:

        # Any unexpected error should make the Lambda
        # invocation fail.
        #
        # This is important because our asynchronous
        # Lambda configuration will retry failed
        # invocations and eventually send the failed
        # event to our SQS DLQ.

        print(
            f"Unexpected processing error: {exc}"
        )

        raise