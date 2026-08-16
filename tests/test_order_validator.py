from src.validators.order_validator import validate_order


def test_valid_order():
    order = {
        "order_id": "O001",
        "customer_id": "C001",
        "product": "Laptop",
        "quantity": "1",
        "amount": "75000",
        "status": "COMPLETED",
    }

    is_valid, reason = validate_order(order)

    assert is_valid is True
    assert reason == ""


def test_missing_order_id():
    order = {
        "customer_id": "C001",
        "product": "Laptop",
        "quantity": "1",
        "amount": "75000",
        "status": "COMPLETED",
    }

    is_valid, reason = validate_order(order)

    assert is_valid is False
    assert reason == "Order_Id is missing"


def test_invalid_quantity():
    order = {
        "order_id": "O001",
        "customer_id": "C001",
        "product": "Laptop",
        "quantity": "-1",
        "amount": "75000",
        "status": "COMPLETED",
    }

    is_valid, reason = validate_order(order)

    assert is_valid is False
    assert reason == "Quantity must be greater than 0"


def test_invalid_amount():
    order = {
        "order_id": "O001",
        "customer_id": "C001",
        "product": "Laptop",
        "quantity": "1",
        "amount": "-100",
        "status": "COMPLETED",
    }

    is_valid, reason = validate_order(order)

    assert is_valid is False
    assert reason == "Amount must be greater than 0"


def test_missing_customer_id():
    order = {
        "order_id": "O001",
        "product": "Laptop",
        "quantity": "1",
        "amount": "75000",
        "status": "COMPLETED",
    }

    is_valid, reason = validate_order(order)

    assert is_valid is False
    assert reason == "Customer_Id is missing"
