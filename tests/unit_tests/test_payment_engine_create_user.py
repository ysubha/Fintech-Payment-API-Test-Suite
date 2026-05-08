import allure
import pytest

from utils.unit_tests_assertions import assert_create_user_successfully, assert_current_balance

USER_ID = 'User001'
INITIAL_BALANCE = 1000


@allure.feature('User Creation-Unit Tests')
@allure.story('Successful creation of user')
@allure.severity(allure.severity_level.CRITICAL)
def test_create_user_success(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


@allure.feature('User Creation-Unit Tests')
@allure.story('User creation failure due to duplicate user.')
@allure.severity(allure.severity_level.NORMAL)
def test_duplicate_user_creation_failure(pay_engine):
    assert_create_user_successfully(pay_engine, USER_ID, INITIAL_BALANCE)
    # TRY TO CREATE DUPLICATE OF USER
    response = pay_engine.create_user(USER_ID, INITIAL_BALANCE)
    assert response['status'] == 'FAILED'
    assert response['reason'] == 'USER_ALREADY_EXISTS'
    assert_current_balance(pay_engine, USER_ID, INITIAL_BALANCE)


@allure.feature('User Creation-Unit Tests')
@allure.story('User creation failure due to invalid balance.')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('balance', [-1000, None, 'abc'])
def test_create_user_with_invalid_balance_failure(pay_engine, balance):
    user_id = 'User001'
    response = pay_engine.create_user(user_id, balance)
    assert response['status'] == 'FAILED'
    assert response['reason'] == 'INVALID_AMOUNT'
