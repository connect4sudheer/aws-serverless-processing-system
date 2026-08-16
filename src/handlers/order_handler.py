# handlers/order_handler.py

from services.s3_service import read_csv
from utils.result_utils import create_processing_result
from validators.order_validator import validate_order


def process_order_data(bucket_name, object_key):
    """
    Read and process order records.

    Invalid orders are recorded as business validation
    errors instead of causing the entire Lambda invocation
    to fail.
    """

    orders = read_csv(
        bucket_name,
        object_key,
    )

    result = create_processing_result(
        source_file=object_key,
        total_records=len(orders),
    )

    for order in orders:

        is_valid, reason = validate_order(
            order
        )

        if is_valid:

            result["valid_records"] += 1

        else:

            result["invalid_records"] += 1

            result["errors"].append(
                {
                    "order_id": order.get(
                        "order_id"
                    ),
                    "reason": reason,
                }
            )

    return result