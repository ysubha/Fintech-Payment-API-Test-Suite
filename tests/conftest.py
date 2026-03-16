import pytest
from services.payment_engine import PaymentEngine
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
        'user_id': 'User001',
        'amount': 1000
    }
    return server_client.post(url, json=user_json)
