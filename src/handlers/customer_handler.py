# handlers/customer_handler.py

from services.s3_service import read_csv
from utils.result_utils import create_processing_result
from validators.customer_validator import validate_customer


def process_customer_data(bucket_name, object_key):
    """
    Read and process customer records.

    Business validation failures are captured in the result.
    They do NOT cause the entire Lambda invocation to fail.
    """

    customers = read_csv(
        bucket_name,
        object_key,
    )

    result = create_processing_result(
        source_file=object_key,
        total_records=len(customers),
    )

    for customer in customers:

        is_valid, reason = validate_customer(
            customer
        )

        if is_valid:

            result["valid_records"] += 1

        else:

            result["invalid_records"] += 1

            result["errors"].append(
                {
                    "customer_id": customer.get(
                        "customer_id"
                    ),
                    "reason": reason,
                }
            )

    return result