import json
import random

import pytest
from playwright.sync_api import sync_playwright

from tests.constants import DEFAULT_USER_ID, DEFAULT_INITIAL_BALANCE
from utils.helper import get_properties


def test_e2e_payment_flow():
    with sync_playwright() as playwright:
        base_url = get_properties('API', 'base_url')
        request = playwright.request.new_context(base_url=base_url)

        user_id = f"User_{random.random()}"
        user = {
            'user_id': user_id,
            'amount': DEFAULT_INITIAL_BALANCE
        }
        header = {"Content-Type": "application/json"}
        # CreateUser
        response = request.post('/users', data=json.dumps(user), headers=header)
        assert response.status == 200

        user['amount'] = 200
        # Process Payment
        response = request.post('/payments', data=json.dumps(user), headers=header)
        assert response.status == 200

        user['txn_id'] = response.json()['txn_id']
        # Refund Payment
        response = request.post('/refunds', data=json.dumps(user), headers=header)
        assert response.status == 200

        # Check Balance
        response = request.get(f'/users/{user_id}/balance')
        assert response.status == 200
        data = response.json()
        assert data['balance'] == pytest.approx(DEFAULT_INITIAL_BALANCE)

# python -m flask --app utils.app:api run --port 5000
# PS C:\Users\Subha\PycharmProjects\Mini Fintech Payment & Order System> $env:PYTHONPATH="."
# PS C:\Users\Subha\PycharmProjects\Mini Fintech Payment & Order System> pytest tests/playwright -v
