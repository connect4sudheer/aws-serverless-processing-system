from src.validators.customer_validator import validate_customer


def test_valid_customer():
    customer = {
        "customer_id": "C001",
        "name": "Jyoti",
        "email": "jyoti@example.com",
        "phone": "9876543210",
        "status": "ACTIVE",
    }

    is_valid, reason = validate_customer(customer)

    assert is_valid is True
    assert reason == ""


def test_missing_customer_id():
    customer = {
        "name": "Jyoti",
        "email": "jyoti@example.com",
        "phone": "9876543210",
        "status": "ACTIVE",
    }

    is_valid, reason = validate_customer(customer)

    assert is_valid is False
    assert reason == "Customer_Id is missing"


def test_invalid_email():
    customer = {
        "customer_id": "C001",
        "name": "Jyoti",
        "email": "invalid-email",
        "phone": "9876543210",
        "status": "ACTIVE",
    }

    is_valid, reason = validate_customer(customer)

    assert is_valid is False
    assert reason == "Invalid Email"


def test_invalid_phone():
    customer = {
        "customer_id": "C001",
        "name": "Jyoti",
        "email": "jyoti@example.com",
        "phone": "12345",
        "status": "ACTIVE",
    }

    is_valid, reason = validate_customer(customer)

    assert is_valid is False
    assert reason == "Invalid Phone"


def test_missing_name():
    customer = {
        "customer_id": "C001",
        "email": "jyoti@example.com",
        "phone": "9876543210",
        "status": "ACTIVE",
    }

    is_valid, reason = validate_customer(customer)

    assert is_valid is False
    assert reason == "Name is missing"
