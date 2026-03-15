import pytest

# TOPIC: User Creation - Tests
def test_create_user_success(pay_engine):
    user_id = "User001"
    amount = 1000

    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    balance_response = pay_engine.get_balance(user_id)
    assert balance_response["status"] == "SUCCESS"
    assert balance_response["balance"] == float(amount)

def test_get_balance_for_user_not_found_failure(pay_engine):
    user_id = "Unknown_user"

    failure_response = pay_engine.get_balance(user_id)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == 'USER_NOT_FOUND'

def test_duplicate_user_creation_failure(pay_engine):
    user_id = "User001"
    amount = 1000

    #CREATE USER
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    #TRY TO CREATE DUPLICATE OF USER
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "FAILED"
    assert response["reason"] == "USER_ALREADY_EXISTS"
    balance_response = pay_engine.get_balance(user_id)
    assert balance_response["balance"] == float(amount)

@pytest.mark.parametrize('balance',[-1000,None,'abc'])
def test_create_user_with_invalid_balance_failure(pay_engine,balance):
    user_id = "User001"
    response = pay_engine.create_user(user_id, balance)
    assert response["status"] == "FAILED"
    assert response["reason"] == "INVALID_AMOUNT"


# TOPIC: Get Balance
def test_get_balance_successfully(pay_engine):
    user_id = "User001"
    amount = 1000

    #CREATE USER
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    # Get Balance
    success_response = pay_engine.get_balance(user_id)
    assert success_response["status"] == "SUCCESS"
    assert success_response["balance"] == pytest.approx(float(amount))
    assert "reason" not in success_response

def test_get_balance_for_unknown_user_failure(pay_engine):
    user_id = "Unknown_user"

    # Get Balance
    failure_response = pay_engine.get_balance(user_id)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == 'USER_NOT_FOUND'


# TOPIC: Process Payment Tests
# Covers Successful payment
@pytest.mark.parametrize('balance',['500',500])
def test_process_payment_success(pay_engine,balance):
    # Create User
    user_id = "User001"
    amount = 1000.0
    response = pay_engine.create_user(user_id,amount)
    assert response["status"] == "SUCCESS"

    # Process Payment
    success_response = pay_engine.process_payment(user_id,balance)
    assert success_response["status"] == "SUCCESS"
    expected_balance = pytest.approx(float(amount) - float(balance))
    assert success_response["balance"] == expected_balance

# Covers Exact balance payment
def test_process_exact_balance_payment_success(pay_engine):
    # Create User
    user_id = "User001"
    amount = 1000
    response = pay_engine.create_user(user_id,amount)
    assert response["status"] == "SUCCESS"

    # Process Payment
    success_response = pay_engine.process_payment(user_id,amount)
    assert success_response["status"] == "SUCCESS"
    assert success_response["balance"] == pytest.approx(0.0)

# Covers Negative/Zero + Invalid payments
@pytest.mark.parametrize('invalid_amount',[0,-200,None,'abc'])
def test_process_invalid_amount_payment_failure(pay_engine, invalid_amount):
    # Create User
    user_id = "User001"
    amount = 1000
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    # Process Payment
    failure_response = pay_engine.process_payment(user_id, invalid_amount)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == "INVALID_AMOUNT"
    success_response = pay_engine.get_balance(user_id)
    assert success_response["status"] == "SUCCESS"
    assert  success_response["balance"] == float(amount)

# Covers Insufficient funds
def test_payment_failure_due_to_insufficient_balance(pay_engine):
    # Create User
    user_id = "User001"
    amount = 1000
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    # Process Payment
    current_payment = float(2*amount)
    failure_response = pay_engine.process_payment(user_id, current_payment)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == "INSUFFICIENT_FUNDS"

    success_response = pay_engine.get_balance(user_id)
    assert success_response["status"] == "SUCCESS"
    assert success_response["balance"]  < current_payment
    assert  success_response['balance'] == float(amount)

def test_payment_failure_for_invalid_amount_and_user_not_found(pay_engine):
    user_id = "Unknown_user"
    balance = -1000

    failure_response = pay_engine.process_payment(user_id,balance)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == 'INVALID_AMOUNT'
    failure_response = pay_engine.process_payment(user_id, 100.0)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == 'USER_NOT_FOUND'

# TOPIC: Refund
# Successful refund
def test_successful_refund_successfully(pay_engine):
    #Create User
    user_id = "User001"
    amount = 1000
    response = pay_engine.create_user(user_id,amount)
    assert response['status'] == "SUCCESS"

    refund_amount = 200
    response = pay_engine.refund_payment(user_id,refund_amount)
    assert response['status'] == "SUCCESS"
    new_balance = pytest.approx(amount+refund_amount)
    assert response['balance'] == new_balance

    response = pay_engine.get_balance(user_id)
    assert response['status'] == "SUCCESS"
    assert response['balance'] == new_balance

# Refund negative amount
def test_refund_failure_for_invalid_amount_and_user_not_found(pay_engine):
    user_id = "Unknown_user"
    amount = -1000
    failure_response = pay_engine.refund_payment(user_id,amount)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == 'INVALID_AMOUNT'
    failure_response = pay_engine.refund_payment(user_id, 100.0)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == 'USER_NOT_FOUND'

@pytest.mark.parametrize('invalid_amount',[0,-200,None,'abc'])
def test_refund_invalid_amount_does_not_change_balance(pay_engine, invalid_amount):
    user_id = "User001"
    amount = 1000
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    failure_response = pay_engine.refund_payment(user_id, invalid_amount)
    assert failure_response["status"] == "FAILED"
    assert failure_response["reason"] == "INVALID_AMOUNT"
    success_response = pay_engine.get_balance(user_id)
    assert success_response["status"] == "SUCCESS"
    assert success_response["balance"] == pytest.approx(amount)

# Multiple sequential payments reduce balance correctly
def test_multiple_sequential_payments_processing_success(pay_engine):
    # Create User
    user_id = "User001"
    current_balance = 1000.0
    response = pay_engine.create_user(user_id,current_balance)
    assert response["status"] == "SUCCESS"

    # Process Multiple Payments
    deduction_amount =100.0
    response = pay_engine.process_payment(user_id,deduction_amount)
    assert response["status"] == "SUCCESS"
    response = pay_engine.process_payment(user_id, deduction_amount)
    assert response["status"] == "SUCCESS"
    response = pay_engine.process_payment(user_id, deduction_amount)
    assert response["status"] == "SUCCESS"

    expected_balance = current_balance - 3*deduction_amount
    success_response = pay_engine.get_balance(user_id)
    assert success_response["status"] == "SUCCESS"
    assert success_response["balance"] == pytest.approx(expected_balance)

# Payment then refund restores balance
def test_payment_and_then_refund_of_balance_successfully(pay_engine):
    user_id = "User001"
    amount = 1000.0
    response = pay_engine.create_user(user_id, amount)
    assert response["status"] == "SUCCESS"

    process_amount = 100.0
    curr_balance = pytest.approx(amount - process_amount)
    pay_response = pay_engine.process_payment(user_id,process_amount)
    assert pay_response["status"] == "SUCCESS"
    assert pay_response["balance"] == curr_balance
    pay_response = pay_engine.get_balance(user_id)
    assert pay_response["balance"] == curr_balance

    refund_response = pay_engine.refund_payment(user_id,process_amount)
    assert refund_response["status"] == "SUCCESS"
    assert refund_response["balance"] == amount
    refund_response = pay_engine.get_balance(user_id)
    assert refund_response["balance"] == amount