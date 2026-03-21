import pytest
from services.payment_engine import PaymentEngine
from tests.constants import DEFAULT_USER_ID, DEFAULT_INITIAL_BALANCE
from utils.app import api


@pytest.fixture
def pay_engine():
    return PaymentEngine()


@pytest.fixture(autouse=True)
def reset_engine():
    from utils.app import pay_engine
    pay_engine.reset()


@pytest.fixture(scope='function')
def server_client():
    with api.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def create_user(server_client):
    url = '/users'
    user_json = {
        'user_id': DEFAULT_USER_ID,
        'amount': DEFAULT_INITIAL_BALANCE
    }
    response = server_client.post(url, json=user_json)
    assert response.status_code == 200, f'user creation failed: {response.get_json()}'
    return response
