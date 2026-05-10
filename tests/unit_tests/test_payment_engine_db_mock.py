from unittest.mock import patch

import pytest


@patch('services.payment_engine.create_user_in_db')
def test_db_failure_on_user_creation_mock(mock_db, pay_engine, fake):
    mock_db.side_effect = Exception('DB is down')
    user_id = fake.user_name()
    initial_balance = 1000
    response = pay_engine.create_user(user_id, initial_balance)

    assert response['status'] == 'SUCCESS'
    assert response['balance'] == initial_balance
    assert response['balance'] == pay_engine.get_balance(user_id)['balance']


@patch('services.payment_engine.insert_transaction_in_db')
def test_transaction_insertion_failure_in_db_mock(mock_db, pay_engine, fake):
    mock_db.side_effect = Exception('DB is down')

    user_id = fake.user_name()
    initial_balance = 1000
    payment = 100
    pay_engine.create_user(user_id, initial_balance)
    response = pay_engine.process_payment(user_id, payment)
    assert response['status'] == 'SUCCESS'
    assert response['balance'] == pytest.approx(initial_balance - payment)
    assert 'txn_id' in response
