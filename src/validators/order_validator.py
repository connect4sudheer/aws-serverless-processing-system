# validators/order_validator.py


def validate_order(order):
    """
    Validate one order record.

    Returns:
        (True, "")
        when valid.

        (False, "reason")
        when invalid.
    """

    # Order ID
    if "order_id" not in order:
        return False, "Order_Id is missing"

    if not order.get("order_id"):
        return False, "Invalid Order_Id"

    # Customer ID
    if "customer_id" not in order:
        return False, "Customer_Id is missing"

    if not order.get("customer_id"):
        return False, "Invalid Customer_Id"

    # Product
    if "product" not in order:
        return False, "Product is missing"

    if not order.get("product"):
        return False, "Invalid Product"

    # Quantity
    if "quantity" not in order:
        return False, "Quantity is missing"

    try:
        quantity = int(order["quantity"])

        if quantity <= 0:
            return False, "Quantity must be greater than 0"

    except (TypeError, ValueError):

        return False, "Quantity must be a valid number"

    # Amount
    if "amount" not in order:
        return False, "Amount is missing"

    try:
        amount = float(order["amount"])

        if amount <= 0:
            return False, "Amount must be greater than 0"

    except (TypeError, ValueError):

        return False, "Amount must be a valid number"

    # Status
    if "status" not in order:
        return False, "Status is missing"

    if not order.get("status"):
        return False, "Invalid Status"

    return True, ""