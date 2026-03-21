from utils.integration_tests_assertions import *


def test_create_user_success(server_client, create_user):
    response = create_user
    assert_user_creation_success(response)


def test_user_creation_missing_json_failure(server_client):
    response = server_client.post('/users')
    assert response.status_code == 415


def test_user_creation_missing_user_id_failure(server_client):
    user_json = {
        'amount': 1000
    }
    response = server_client.post('/users', json=user_json)
    assert_user_creation_failure(response)


def test_user_creation_missing_amount_failure(server_client):
    user_json = {
        'user_id': 'User001'
    }
    response = server_client.post('/users', json=user_json)
    assert_user_creation_failure(response)


@pytest.mark.parametrize('amount', [-200, None, 'abc'])
def test_user_creation_invalid_amount_failure(server_client, amount):
    user_json = {
        'user_id': 'User001',
        'amount': amount
    }
    response = server_client.post('/users', json=user_json)
    assert_user_creation_failure(response)


def test_duplicate_user_creation_failure(server_client):
    user_json = {
        'user_id': 'User001',
        'amount': 1000
    }
    response = server_client.post('/users', json=user_json)
    assert_user_creation_success(response)

    duplicate_response = server_client.post('/users', json=user_json)
    assert_user_creation_failure(duplicate_response)
