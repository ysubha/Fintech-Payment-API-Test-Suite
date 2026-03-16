# TOPIC: Process Payment Tests
# Covers Successful payment
import pytest

from utils.unit_tests_assertions import assert_create_user_successfully, assert_payment_process_successfully, \
    assert_payment_process_failure, assert_current_balance

USER_ID = 'User001'
INITIAL_BALANCE = 1000
AMOUNT = 200


# Also Covers Exact balance payment
@pytest.mark.parametrize('balance', ['500', 500, 0])
def test_process_payment_success(pay_engine, balance):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_payment_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - AMOUNT)


# Covers Negative/Zero + Invalid payments
@pytest.mark.parametrize('invalid_amount', [0, -200, None, 'abc'])
def test_process_invalid_amount_payment_failure(pay_engine, invalid_amount):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_payment_process_failure(pay_engine, USER_ID, invalid_amount, 'INVALID_AMOUNT')
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


# Covers Insufficient funds
def test_payment_failure_due_to_insufficient_balance(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)

    current_payment = 2 * INITIAL_BALANCE
    assert_payment_process_failure(pay_engine, USER_ID, current_payment, 'INSUFFICIENT_FUNDS')
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


def test_payment_failure_for_invalid_amount_and_user_not_found(pay_engine):
    user_id = "Unknown_user"
    invalid_amount = -1000

    assert_payment_process_failure(pay_engine, USER_ID, invalid_amount, 'INVALID_AMOUNT')
    assert_payment_process_failure(pay_engine, user_id, AMOUNT, 'USER_NOT_FOUND')
