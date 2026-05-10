import uuid

import pytest

from tests.constants import DEFAULT_USER_ID, DEFAULT_INITIAL_BALANCE
from utils.integration_tests_assertions import assert_user_creation_success


def test_duplicate_payment(server_client, create_user):
    idempotency_key = str(uuid.uuid4())
    assert_user_creation_success(create_user)
    payment_amount = 100

    payment_json = {
        'user_id': DEFAULT_USER_ID,
        'amount': payment_amount
    }

    # INITIAL PAYMENT
    headers = {'Idempotency-Key': idempotency_key}
    response = server_client.post('/payments', json=payment_json, headers=headers)
    response_data_of_initial_payment = response.get_json()
    assert response.status_code == 200
    assert response_data_of_initial_payment['status'] == 'SUCCESS'
    assert response_data_of_initial_payment['balance'] == pytest.approx(DEFAULT_INITIAL_BALANCE - payment_amount)
    # DUPLICATE PAYMENT
    response_duplicate = server_client.post('/payments', json=payment_json, headers=headers)
    assert response_duplicate.status_code == 200
    response_data_of_duplicate_payment = response_duplicate.get_json()
    assert response_data_of_duplicate_payment['status'] == 'SUCCESS'
    assert response_data_of_duplicate_payment['balance'] == response_data_of_initial_payment['balance']
    assert response_data_of_initial_payment == response_data_of_duplicate_payment


def test_fresh_payments(server_client, create_user):
    idempotency_key1 = str(uuid.uuid4())
    idempotency_key2 = str(uuid.uuid4())
    assert_user_creation_success(create_user)
    payment_amount = 100

    payment_json = {
        'user_id': DEFAULT_USER_ID,
        'amount': payment_amount
    }
    # INITIAL PAYMENT
    headers = {'Idempotency-Key': idempotency_key1}
    response = server_client.post('/payments', json=payment_json, headers=headers)
    response_data_of_initial_payment = response.get_json()
    assert response.status_code == 200
    assert response_data_of_initial_payment['status'] == 'SUCCESS'
    assert response_data_of_initial_payment['balance'] == pytest.approx(DEFAULT_INITIAL_BALANCE - payment_amount)

    # SECOND PAYMENT
    headers = {'Idempotency-Key': idempotency_key2}
    response_duplicate = server_client.post('/payments', json=payment_json, headers=headers)
    assert response_duplicate.status_code == 200
    response_data_of_duplicate_payment = response_duplicate.get_json()
    assert response_data_of_duplicate_payment['status'] == 'SUCCESS'
    assert response_data_of_duplicate_payment['balance'] == pytest.approx(DEFAULT_INITIAL_BALANCE - 2 * payment_amount)
    assert response_data_of_initial_payment['txn_id'] != response_data_of_duplicate_payment['txn_id']


def test_duplicate_payment_with_diff_payment_amounts(server_client, create_user):
    idempotency_key = str(uuid.uuid4())
    assert_user_creation_success(create_user)
    payment_amount1 = 100
    payment_amount2 = 200

    payment_json = {
        'user_id': DEFAULT_USER_ID,
        'amount': payment_amount1
    }
    # INITIAL PAYMENT
    headers = {'Idempotency-Key': idempotency_key}
    response = server_client.post('/payments', json=payment_json, headers=headers)
    response_data_of_initial_payment = response.get_json()
    assert response.status_code == 200
    assert response_data_of_initial_payment['status'] == 'SUCCESS'
    assert response_data_of_initial_payment['balance'] == pytest.approx(DEFAULT_INITIAL_BALANCE - payment_amount1)

    # DUPLICATE PAYMENT - with diff. payment amount, still since Idempotency_key is same, the second payment doesn't occur
    payment_json = {
        'user_id': DEFAULT_USER_ID,
        'amount': payment_amount2
    }
    response_duplicate = server_client.post('/payments', json=payment_json, headers=headers)
    assert response_duplicate.status_code == 200
    response_data_of_duplicate_payment = response_duplicate.get_json()
    assert response_data_of_duplicate_payment['status'] == 'SUCCESS'
    assert response_data_of_duplicate_payment['balance'] == response_data_of_initial_payment['balance']
    assert response_data_of_initial_payment == response_data_of_duplicate_payment
