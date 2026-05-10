import uuid

import allure
from jsonschema import validate

from tests.constants import DEFAULT_USER_ID
from utils.integration_tests_assertions import assert_user_creation_success


@allure.feature('Schema Validation-Integration Tests')
@allure.story('Successful schema structure validation')
@allure.severity(allure.severity_level.CRITICAL)
def test_base_success_schema_structure(create_user):
    response = create_user
    success_schema = {
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
            'balance': {'type': 'number'}

        },
        'required': ['status', 'balance']
    }
    assert response.status_code == 200
    validate(instance=response.get_json(), schema=success_schema)


@allure.feature('Schema Validation-Integration Tests')
@allure.story('Successful payment schema structure validation')
@allure.severity(allure.severity_level.CRITICAL)
def test_payment_success_schema_structure(create_user, server_client):
    assert_user_creation_success(create_user)
    payment_json = {
        'user_id': DEFAULT_USER_ID,
        'amount': 500
    }
    idempotency_key = str(uuid.uuid4())
    headers = {'Idempotency-Key': idempotency_key}
    payment_response = server_client.post('/payments', json=payment_json, headers=headers)
    success_schema = {
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
            'balance': {'type': 'number'},
            'txn_id': {'type': 'string'}
        },
        'required': ['status', 'balance', 'txn_id']
    }
    assert payment_response.status_code == 200
    validate(instance=payment_response.get_json(), schema=success_schema)


@allure.feature('Schema Validation-Integration Tests')
@allure.story('Failed schema structure validation')
@allure.severity(allure.severity_level.CRITICAL)
def test_failure_schema_structure(server_client):
    idempotency_key = str(uuid.uuid4())
    headers = {'Idempotency-Key': idempotency_key}
    response = server_client.post('/payments', json={'amount': 1000}, headers=headers)
    failure_schema = {
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
            'reason': {'type': 'string'}
        },
        'required': ['status', 'reason']
    }
    assert response.status_code == 400
    validate(instance=response.get_json(), schema=failure_schema)
