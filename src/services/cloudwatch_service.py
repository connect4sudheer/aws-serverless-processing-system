# services/cloudwatch_service.py

import boto3

from config import CLOUDWATCH_NAMESPACE
from utils.result_utils import calculate_invalid_percentage


cloudwatch_client = boto3.client("cloudwatch")


def publish_processing_metrics(result, file_type):
    """
    Publish application-level processing metrics
    to Amazon CloudWatch.

    Metrics:
        FilesProcessed
        TotalRecords
        InvalidRecords
        InvalidRecordPercentage
    """

    total_records = result["total_records"]
    invalid_records = result["invalid_records"]

    invalid_percentage = calculate_invalid_percentage(
        result
    )

    print(
        f"Publishing CloudWatch metrics: "
        f"file_type={file_type}, "
        f"total={total_records}, "
        f"invalid={invalid_records}, "
        f"invalid_percentage={invalid_percentage:.2f}"
    )

    try:

        cloudwatch_client.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,

            MetricData=[
                {
                    "MetricName": "FilesProcessed",
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [
                        {
                            "Name": "FileType",
                            "Value": file_type,
                        }
                    ],
                },
                {
                    "MetricName": "TotalRecords",
                    "Value": total_records,
                    "Unit": "Count",
                    "Dimensions": [
                        {
                            "Name": "FileType",
                            "Value": file_type,
                        }
                    ],
                },
                {
                    "MetricName": "InvalidRecords",
                    "Value": invalid_records,
                    "Unit": "Count",
                    "Dimensions": [
                        {
                            "Name": "FileType",
                            "Value": file_type,
                        }
                    ],
                },
                {
                    "MetricName": "InvalidRecordPercentage",
                    "Value": invalid_percentage,
                    "Unit": "Percent",
                    "Dimensions": [
                        {
                            "Name": "FileType",
                            "Value": file_type,
                        }
                    ],
                },
            ],
        )

    except Exception as exc:

        # Monitoring should not make an otherwise successful
        # business transaction fail.
        print(
            f"WARNING: Failed to publish CloudWatch "
            f"metrics: {exc}"
        )