from utils.assertions import *

USER_ID = 'User001'
INITIAL_BALANCE = 1000
REFUND_AMOUNT = 500
AMOUNT = 500

def test_refund_success(server_client, create_user):
    assert create_user.status_code == 200
    refund_json = {
        'user_id': USER_ID,
        'amount': REFUND_AMOUNT
    }
    assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + REFUND_AMOUNT, USER_ID)


def test_multiple_refunds_success(server_client, create_user):
    assert create_user.status_code == 200
    refund_json = {
        'user_id': USER_ID,
        'amount': REFUND_AMOUNT
    }

    assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + REFUND_AMOUNT, USER_ID)
    assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + 2 * REFUND_AMOUNT, USER_ID)
    assert_successful_refund_response(server_client, refund_json, INITIAL_BALANCE + 3 * REFUND_AMOUNT, USER_ID)


def test_refund_after_payment_restores_balance_success(server_client, create_user):
    assert create_user.status_code == 200
    request_json = {
        'user_id': USER_ID,
        'amount': REFUND_AMOUNT
    }

    payment_response = server_client.post('/payments', json=request_json)
    assert payment_response.status_code == 200
    payment_response_json = payment_response.get_json()
    assert payment_response_json['status'] == 'SUCCESS'
    assert payment_response_json['balance'] == pytest.approx(INITIAL_BALANCE - REFUND_AMOUNT)
    assert_balance(server_client, INITIAL_BALANCE - REFUND_AMOUNT, USER_ID)

    assert_successful_refund_response(server_client, request_json, INITIAL_BALANCE, USER_ID)


def test_missing_amount_refund_failure(server_client, create_user):
    assert create_user.status_code == 200
    refund_json = {
        'user_id': USER_ID,
    }
    assert_failed_refund_response(server_client, refund_json, 'INVALID_INPUT', INITIAL_BALANCE, USER_ID)


def test_missing_user_id_failure(server_client, create_user):
    assert create_user.status_code == 200
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
        'amount': refund_amount
    }
    assert_failed_refund_response(server_client, refund_json, 'INVALID_AMOUNT', INITIAL_BALANCE, USER_ID)


def test_user_not_found_failure(server_client):
    refund_json = {
        'user_id': USER_ID,
        'amount': REFUND_AMOUNT
    }
    refund_response = server_client.post('/refunds', json=refund_json)
    assert refund_response.status_code == 400
    refund_data = refund_response.get_json()
    assert refund_data['status'] == 'FAILED'
    assert refund_data['reason'] == 'USER_NOT_FOUND'



def test_payment_refund_mixed_sequence(server_client, create_user):
    assert create_user.status_code == 200

    request_json = {
        'user_id': USER_ID,
        'amount': AMOUNT
    }
    assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - AMOUNT, USER_ID)
    assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - 2 * AMOUNT, USER_ID)
    assert_successful_refund_response(server_client, request_json, INITIAL_BALANCE - AMOUNT, USER_ID)
    assert_successful_refund_response(server_client, request_json, INITIAL_BALANCE, USER_ID)
    assert_successful_payment_response(server_client, request_json, INITIAL_BALANCE - AMOUNT, USER_ID)
    assert_successful_refund_response(server_client, request_json, INITIAL_BALANCE, USER_ID)
