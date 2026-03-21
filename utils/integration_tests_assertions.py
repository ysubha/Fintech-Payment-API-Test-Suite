import pytest


def assert_user_creation_success(response):
    assert response.status_code == 200
    assert response.get_json()['status'] == 'SUCCESS'


def assert_user_creation_failure(response):
    assert response.status_code == 400
    assert response.get_json()['status'] == 'FAILED'


def assert_balance(server_client, balance, user_id):
    balance_response = server_client.get(f'/users/{user_id}/balance')
    assert balance_response.status_code == 200
    balance_json = balance_response.get_json()
    assert balance_json['status'] == 'SUCCESS'
    assert balance_json['balance'] == pytest.approx(balance)


def assert_successful_payment_response(server_client, payment_json, balance, user_id):
    payment_response = server_client.post('/payments', json=payment_json)
    assert payment_response.status_code == 200
    payment_response_json = payment_response.get_json()
    assert payment_response_json['status'] == 'SUCCESS'
    assert payment_response_json['balance'] == pytest.approx(balance)

    assert_balance(server_client, balance, user_id)
    return payment_response_json['txn_id']


def assert_failed_payment_response(server_client, payment_json, reason, balance, user_id):
    payment_response = server_client.post('/payments', json=payment_json)
    assert payment_response.status_code == 400
    payment_response_json = payment_response.get_json()
    assert payment_response_json['status'] == 'FAILED'
    assert payment_response_json['reason'] == reason

    assert_balance(server_client, balance, user_id)


def assert_successful_refund_response(server_client, refund_json, net_balance, user_id):
    refund_response = server_client.post('/refunds', json=refund_json)
    assert refund_response.status_code == 200
    refund_data = refund_response.get_json()
    assert refund_data['status'] == 'SUCCESS'
    assert refund_data['balance'] == pytest.approx(net_balance)
    print(refund_data['balance'],pytest.approx(net_balance))
    assert_balance(server_client, net_balance, user_id)


def assert_failed_refund_response(server_client, refund_json, reason, net_balance, user_id):
    refund_response = server_client.post('/refunds', json=refund_json)
    assert refund_response.status_code == 400
    refund_data = refund_response.get_json()
    assert refund_data['status'] == 'FAILED'
    assert refund_data['reason'] == reason

    assert_balance(server_client, net_balance, user_id)
