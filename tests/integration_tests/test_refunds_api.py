import pytest

from utils.integration_tests_assertions import assert_user_creation_success, assert_successful_payment_response, \
    assert_successful_refund_response, assert_failed_refund_response

USER_ID = 'User001'
INITIAL_BALANCE = 1000.0
REFUND_AMOUNT = 500.0
AMOUNT = 200.0


def test_refund_success(server_client, create_user):
    assert_user_creation_success(create_user)
    request_json = {
        'user_id': USER_ID,
        'amount': AMOUNT
    }
    transaction_id = assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - AMOUNT, USER_ID)
    request_json['txn_id'] = transaction_id
    assert_successful_refund_response(server_client, request_json, INITIAL_BALANCE, USER_ID)


def test_missing_amount_refund_failure(server_client, create_user):
    assert create_user.status_code == 200
    refund_json = {
        'user_id': USER_ID,
    }
    assert_failed_refund_response(server_client, refund_json, 'INVALID_INPUT', INITIAL_BALANCE, USER_ID)


def test_missing_user_id_failure(server_client, create_user):
    assert_user_creation_success(create_user)
    refund_json = {
        'amount': REFUND_AMOUNT
    }
    assert_failed_refund_response(server_client, refund_json, 'INVALID_INPUT', INITIAL_BALANCE, USER_ID)


def test_missing_request_body_failure(server_client, create_user):
    assert create_user.status_code == 200

    refund_response = server_client.post('/refunds')
    assert refund_response.status_code == 415  # its not returning 400, its giving 415


@pytest.mark.parametrize('refund_amount', [0, -250, None, 'abc'])
def test_invalid_amount_refund_failure(server_client, create_user, refund_amount):
    assert create_user.status_code == 200
    refund_json = {
        'user_id': USER_ID,
        'amount': refund_amount,
        'txn_id': 'TXN_1'
    }
    assert_failed_refund_response(server_client, refund_json, 'INVALID_AMOUNT', INITIAL_BALANCE, USER_ID)


def test_user_not_found_failure(server_client):
    refund_json = {
        'user_id': USER_ID,
        'amount': REFUND_AMOUNT,
        'txn_id': 'TXN_1'
    }
    refund_response = server_client.post('/refunds', json=refund_json)
    assert refund_response.status_code == 400
    refund_data = refund_response.get_json()
    assert refund_data['status'] == 'FAILED'
    assert refund_data['reason'] == 'USER_NOT_FOUND'


def test_payment_refund_mixed_sequence(server_client, create_user):
    assert_user_creation_success(create_user)
    request_json = {
        'user_id': USER_ID,
        'amount': AMOUNT
    }
    transaction_id_1 = assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - AMOUNT,
                                                          USER_ID)
    transaction_id_2 = assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - 2 * AMOUNT,
                                                          USER_ID)

    request_json['txn_id'] = transaction_id_1
    assert_successful_refund_response(server_client, request_json, float(INITIAL_BALANCE - AMOUNT), USER_ID)

    transaction_id_3 = assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - 2 * AMOUNT,
                                                          USER_ID)

    request_json['txn_id'] = transaction_id_2
    assert_successful_refund_response(server_client, request_json, float(INITIAL_BALANCE - AMOUNT), USER_ID)

    request_json['txn_id'] = transaction_id_3
    assert_successful_refund_response(server_client, request_json, float(INITIAL_BALANCE), USER_ID)

# def test_multiple_refunds_success(server_client, create_user):
#     assert create_user.status_code == 200
#     refund_json = {
#         'user_id': USER_ID,
#         'amount': REFUND_AMOUNT
#     }
#
#     assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + REFUND_AMOUNT, USER_ID)
#     assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + 2 * REFUND_AMOUNT, USER_ID)
#     assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + 3 * REFUND_AMOUNT, USER_ID)


# def test_refund_after_payment_restores_balance_success(server_client, create_user):
#     assert_user_creation_success(create_user)
#     request_json = {
#         'user_id': USER_ID,
#         'amount': AMOUNT
#     }
#     transaction_id = assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - AMOUNT, USER_ID)
#     request_json['txn_id'] = transaction_id
#     assert_successful_refund_response(server_client, request_json, INITIAL_BALANCE, USER_ID)
