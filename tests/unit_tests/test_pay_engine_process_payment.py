import allure
import pytest

from utils.unit_tests_assertions import assert_create_user_successfully, assert_payment_process_successfully, \
    assert_payment_process_failure, assert_current_balance

USER_ID = 'User001'
INITIAL_BALANCE = 1000
AMOUNT = 200


@allure.feature('Payment Process-Unit Tests')
@allure.story('Successful payment process')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('balance', [500, INITIAL_BALANCE])
def test_process_payment_success(pay_engine, balance):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_payment_process_successfully(pay_engine, USER_ID, balance, INITIAL_BALANCE - balance)


@allure.feature('Payment Process-Unit Tests')
@allure.story('Failure of payment due to invalid amount')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('invalid_amount', [0, -200, None, 'abc'])
def test_process_invalid_amount_payment_failure(pay_engine, invalid_amount):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_payment_process_failure(pay_engine, USER_ID, invalid_amount, 'INVALID_AMOUNT')
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


@allure.feature('Payment Process-Unit Tests')
@allure.story('Failure of payment due to insufficient balance')
@allure.severity(allure.severity_level.NORMAL)
def test_payment_failure_due_to_insufficient_balance(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)

    current_payment = 2 * INITIAL_BALANCE
    assert_payment_process_failure(pay_engine, USER_ID, current_payment, 'INSUFFICIENT_FUNDS')
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


@allure.feature('Payment Process-Unit Tests')
@allure.story('Failure of payment due to invalid amount and user not found')
@allure.severity(allure.severity_level.NORMAL)
def test_payment_failure_for_invalid_amount_and_user_not_found(pay_engine):
    user_id = "Unknown_user"
    invalid_amount = -1000

    assert_payment_process_failure(pay_engine, USER_ID, invalid_amount, 'INVALID_AMOUNT')
    assert_payment_process_failure(pay_engine, user_id, AMOUNT, 'USER_NOT_FOUND')
