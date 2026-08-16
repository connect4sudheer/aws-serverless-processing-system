# utils/result_utils.py


def create_processing_result(source_file, total_records):
    """
    Create the standard result structure used by
    both customer and order processing.
    """

    return {
        "source_file": source_file,
        "total_records": total_records,
        "valid_records": 0,
        "invalid_records": 0,
        "status": "COMPLETED",
        "errors": [],
    }


def calculate_invalid_percentage(result):
    """
    Calculate the percentage of invalid records.

    Example:
        Total records = 100
        Invalid records = 5

        Result = 5%
    """

    total_records = result["total_records"]
    invalid_records = result["invalid_records"]

    if total_records == 0:
        return 0.0

    return (
        invalid_records / total_records
    ) * 100