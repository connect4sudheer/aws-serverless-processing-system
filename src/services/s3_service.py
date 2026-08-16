# services/s3_service.py

import csv
from io import StringIO

import boto3


# Create the client outside the Lambda handler.
# Lambda can reuse the client when the execution environment
# is reused, which avoids creating a new client for every request.
s3_client = boto3.client("s3")


def read_file(bucket_name, object_key):
    """
    Read a file from S3 and return its content as text.

    Raises:
        Exception: If S3 cannot retrieve the object.
    """

    try:

        print(
            f"Reading file from S3: "
            f"s3://{bucket_name}/{object_key}"
        )

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key,
        )

        content = response["Body"].read().decode("utf-8")

        return content

    except s3_client.exceptions.NoSuchKey as exc:

        raise FileNotFoundError(
            f"S3 object not found: {object_key}"
        ) from exc

    except Exception as exc:

        raise RuntimeError(
            f"Failed to read S3 object "
            f"{object_key}: {exc}"
        ) from exc


def read_csv(bucket_name, object_key):
    """
    Read a CSV file from S3 and convert each row
    into a dictionary.
    """

    try:

        content = read_file(
            bucket_name,
            object_key,
        )

        csv_reader = csv.DictReader(
            StringIO(content)
        )

        return list(csv_reader)

    except csv.Error as exc:

        raise ValueError(
            f"Invalid CSV file: {object_key}: {exc}"
        ) from exc

    except Exception:
        # Preserve the original exception so the Lambda
        # handler can log and handle it correctly.
        raise


def save_json(bucket_name, object_key, data):
    """
    Save a Python dictionary as a JSON file in S3.
    """

    import json

    try:

        print(
            f"Saving processing result to: "
            f"s3://{bucket_name}/{object_key}"
        )

        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json.dumps(data),
            ContentType="application/json",
        )

    except Exception as exc:

        raise RuntimeError(
            f"Failed to save result to S3 "
            f"{object_key}: {exc}"
        ) from exc