import pytest


def assert_create_user_successfully(pay_engine, user_id, initial_balance):
    response = pay_engine.create_user(user_id, initial_balance)
    assert response['status'] == 'SUCCESS'


def assert_current_balance(pay_engine, user_id, net_balance):
    response = pay_engine.get_balance(user_id)
    assert response['status'] == 'SUCCESS'
    assert response['balance'] == pytest.approx(net_balance)
    assert 'reason' not in response


def assert_payment_process_successfully(pay_engine, user_id, amount, net_balance):
    success_response, transaction_id = pay_engine.process_payment(user_id, amount)
    assert success_response['status'] == 'SUCCESS'
    expected_balance = pytest.approx(net_balance)
    assert success_response['balance'] == expected_balance

    assert_current_balance(pay_engine, user_id, net_balance)
    return transaction_id


def assert_refund_process_successfully(pay_engine, user_id, amount, net_balance, payment_txn_id):
    response = pay_engine.refund_payment(user_id, amount, payment_txn_id)
    assert response['status'] == 'SUCCESS'
    assert response['balance'] == pytest.approx(net_balance)
    assert_current_balance(pay_engine, user_id, net_balance)


def assert_refund_process_failure(pay_engine, user_id, amount, payment_txn_id, reject_reason):
    failure_response = pay_engine.refund_payment(user_id, amount, payment_txn_id)
    assert failure_response['status'] == 'FAILED'
    assert failure_response['reason'] == reject_reason
