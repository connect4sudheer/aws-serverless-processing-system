# validators/customer_validator.py

import re


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def validate_customer(customer):
    """
    Validate one customer record.

    Returns:
        (True, "")
        when the record is valid.

        (False, "reason")
        when the record is invalid.
    """

    # Customer ID validation
    if "customer_id" not in customer:
        return False, "Customer_Id is missing"

    if not customer.get("customer_id"):
        return False, "Invalid Customer_Id"

    # Name validation
    if "name" not in customer:
        return False, "Name is missing"

    if not customer.get("name"):
        return False, "Invalid Name"

    # Email validation
    if "email" not in customer:
        return False, "Email is missing"

    email = customer.get("email")

    if not email or not EMAIL_PATTERN.match(email):
        return False, "Invalid Email"

    # Phone validation
    if "phone" not in customer:
        return False, "Phone is missing"

    phone = customer.get("phone")

    if not phone or len(phone) != 10:
        return False, "Invalid Phone"

    # Status validation
    if "status" not in customer:
        return False, "Status is missing"

    if not customer.get("status"):
        return False, "Invalid Status"

    return True, ""