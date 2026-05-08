import allure

from utils.unit_tests_assertions import assert_create_user_successfully, assert_current_balance


@allure.feature('Balance Retrieval-Unit Tests')
@allure.story('Successful retrieval of balance')
@allure.severity(allure.severity_level.CRITICAL)
def test_get_balance_successfully(pay_engine):
    user_id = 'User001'
    initial_balance = 1000
    assert_create_user_successfully(pay_engine, user_id, initial_balance)
    assert_current_balance(pay_engine, user_id, initial_balance)


@allure.feature('Balance Retrieval-Unit Tests')
@allure.story('Failed retrieval of balance for Unknown user')
@allure.severity(allure.severity_level.NORMAL)
def test_get_balance_for_unknown_user_failure(pay_engine):
    user_id = 'Unknown_user'

    # Get Balance
    failure_response = pay_engine.get_balance(user_id)
    assert failure_response['status'] == 'FAILED'
    assert failure_response['reason'] == 'USER_NOT_FOUND'
