import allure
import pytest

from utils.unit_tests_assertions import assert_create_user_successfully, assert_payment_process_successfully, \
    assert_refund_process_successfully, assert_refund_process_failure, assert_current_balance

USER_ID = "User001"
INITIAL_BALANCE = 1000.0
AMOUNT = 200


@allure.feature('Process Refunds-Unit Tests')
@allure.story('Successful Refund Process')
@allure.severity(allure.severity_level.CRITICAL)
def test_successful_refund_successfully(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    transaction_id = assert_payment_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - AMOUNT)
    assert_refund_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE, transaction_id)


@allure.feature('Process Refunds-Unit Tests')
@allure.story('Refund process failure due to invalid amount or user not found. ')
@allure.severity(allure.severity_level.NORMAL)
def test_refund_failure_for_invalid_amount_and_user_not_found(pay_engine):
    user_id = "Unknown_user"
    amount = -1000
    payment_txn_id = 'TXN_1'
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_refund_process_failure(pay_engine, USER_ID, amount, payment_txn_id, 'INVALID_AMOUNT')
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_refund_process_failure(pay_engine, user_id, AMOUNT, payment_txn_id, 'USER_NOT_FOUND')


@allure.feature('Process Refunds-Unit Tests')
@allure.story('Refund process failure due to invalid amount')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('invalid_amount', [0, -200, None, 'abc'])
def test_refund_invalid_amount_does_not_change_balance(pay_engine, invalid_amount):
    payment_txn_id = 'TXN_1'
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_refund_process_failure(pay_engine, USER_ID, invalid_amount, payment_txn_id, 'INVALID_AMOUNT')
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


@allure.feature('Process Refunds-Unit Tests')
@allure.story('Multiple sequential payments performed successfully.')
@allure.severity(allure.severity_level.CRITICAL)
def test_multiple_sequential_payments_processing_success(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    transaction_id1 = assert_payment_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - AMOUNT)
    transaction_id2 = assert_payment_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - 2 * AMOUNT)
    transaction_id3 = assert_payment_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - 3 * AMOUNT)
    assert_refund_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - 2 * AMOUNT, transaction_id1)
    assert_refund_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - 1 * AMOUNT, transaction_id2)
    assert_refund_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE, transaction_id3)


@allure.feature('Process Refunds-Unit Tests')
@allure.story('Successful payment and refund process to restore balance.')
@allure.severity(allure.severity_level.CRITICAL)
def test_payment_and_then_refund_of_balance_successfully(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)

    transaction_id = assert_payment_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE - AMOUNT)
    assert_refund_process_successfully(pay_engine, USER_ID, AMOUNT, INITIAL_BALANCE, transaction_id)
