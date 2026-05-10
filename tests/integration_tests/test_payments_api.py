import uuid

import allure
import pytest

from utils.integration_tests_assertions import assert_user_creation_success, assert_successful_payment_response, \
    assert_failed_payment_response

USER_ID = 'User001'
INITIAL_BALANCE = 1000
PAYMENT_AMOUNT = 500


@allure.feature('Process Payments-Integration Tests')
@allure.story('Successful payment process')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize('payment_amount', [250, 1000])
def test_process_payment_success(server_client, create_user, payment_amount):
    assert_user_creation_success(create_user)

    payment_json = {
        'user_id': USER_ID,
        'amount': payment_amount
    }
    assert_successful_payment_response(server_client, payment_json, INITIAL_BALANCE - payment_amount, USER_ID)


@allure.feature('Process Payments-Integration Tests')
@allure.story('Payment process failure due to invalid amount ')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('payment_amount', [0, -1000, None, 'abc'])
def test_process_invalid_amount_failure(server_client, create_user, payment_amount):
    assert create_user.status_code == 200

    payment_json = {
        'user_id': USER_ID,
        'amount': payment_amount
    }
    assert_failed_payment_response(server_client, payment_json, 'INVALID_AMOUNT', INITIAL_BALANCE, USER_ID)


@allure.feature('Process Payments-Integration Tests')
@allure.story('Payment process failure due to Insufficient funds.')
@allure.severity(allure.severity_level.NORMAL)
def test_payment_insufficient_funds_failure(server_client, create_user):
    assert create_user.status_code == 200

    payment_json = {
        'user_id': USER_ID,
        'amount': 2000
    }
    assert_failed_payment_response(server_client, payment_json, 'INSUFFICIENT_FUNDS', INITIAL_BALANCE, USER_ID)


@allure.feature('Process Payments-Integration Tests')
@allure.story('Payment process failure due to User not found.')
@allure.severity(allure.severity_level.NORMAL)
def test_payment_user_not_found_failure(server_client):
    payment_json = {
        'user_id': USER_ID,
        'amount': 200
    }
    idempotency_key = str(uuid.uuid4())
    headers = {'Idempotency-Key': idempotency_key}
    payment_response = server_client.post('/payments', json=payment_json, headers=headers)
    assert payment_response.status_code == 400
    payment_response_json = payment_response.get_json()
    assert payment_response_json['status'] == 'FAILED'
    assert payment_response_json['reason'] == 'USER_NOT_FOUND'


@allure.feature('Process Payments-Integration Tests')
@allure.story('Payment process failure due to Missing amount details')
@allure.severity(allure.severity_level.NORMAL)
def test_payment_missing_amount_details_failure(server_client, create_user):
    assert create_user.status_code == 200

    payment_json = {
        'user_id': USER_ID
    }
    assert_failed_payment_response(server_client, payment_json, 'INVALID_INPUT', INITIAL_BALANCE, USER_ID)


@allure.feature('Process Payments-Integration Tests')
@allure.story('Payment process failure due to Missing user details')
@allure.severity(allure.severity_level.NORMAL)
def test_payment_missing_user_details_failure(server_client, create_user):
    assert create_user.status_code == 200

    payment_json = {
        'amount': 250
    }
    assert_failed_payment_response(server_client, payment_json, 'INVALID_INPUT', INITIAL_BALANCE, USER_ID)


@allure.feature('Process Payments-Integration Tests')
@allure.story('Successful Multiple Sequential Payment Processes')
@allure.severity(allure.severity_level.CRITICAL)
def test_multiple_sequential_payments(server_client, create_user):
    assert create_user.status_code == 200

    payment_json = {
        'user_id': USER_ID,
        'amount': 500
    }
    assert_successful_payment_response(server_client, payment_json, 500, USER_ID)
    assert_successful_payment_response(server_client, payment_json, 0, USER_ID)
    assert_failed_payment_response(server_client, payment_json, 'INSUFFICIENT_FUNDS', 0, USER_ID)
