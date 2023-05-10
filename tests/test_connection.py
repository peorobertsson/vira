from vira import VIRA
from vira import VIRAError
import pytest

from tests.conftest import (
    VIRA_URL,
    VIRA_TEST_URL,
    VIRA_TEST_USER,
    VIRA_TEST_USER_PASSWORD,
    VIRA_TEST_ACCESS_TOKEN,
)


# Production VIRA tests
@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_to_production_with_cridentials(no_environment_variables_set):
    vira = VIRA(VIRA_URL)
    vira.connect(user=VIRA_TEST_USER, password=VIRA_TEST_USER_PASSWORD)


@pytest.mark.skip("Fix this. monkeypatch can't emulate getpass.getpass() input.")
@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_to_production_using_console_input(
    no_environment_variables_set, monkeypatch
):
    inputs = iter([VIRA_TEST_USER, VIRA_TEST_USER_PASSWORD])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    vira = VIRA(VIRA_URL)
    vira.connect()


@pytest.mark.usefixtures("correct_test_environment_variables_set")
def test_connection_to_production_with_credentials_using_env_vars(
    correct_test_environment_variables_set,
):
    vira = VIRA(VIRA_URL)
    vira.connect()


# QA Environment tests
@pytest.mark.skip("QA Environment does not support USER / PW credentials")
@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_credentials(no_environment_variables_set):
    vira = VIRA(VIRA_TEST_URL)
    vira.connect(user=VIRA_TEST_USER, password=VIRA_TEST_USER_PASSWORD)


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_token(no_environment_variables_set):
    vira = VIRA(VIRA_TEST_URL)
    vira.connect_with_token(token=VIRA_TEST_ACCESS_TOKEN)


@pytest.mark.usefixtures("correct_test_environment_variables_set")
def test_connection_with_token_using_env_vars(correct_test_environment_variables_set):
    vira = VIRA()
    vira.connect_with_token()


@pytest.mark.usefixtures("correct_test_environment_variables_set")
def test_failed_connection(correct_test_environment_variables_set):
    vira = VIRA(VIRA_TEST_URL)
    with pytest.raises(VIRAError) as e_info:
        # Even with the correct environment variables set, parameters take precidence
        vira.connect(user="VIRA_TEST_USER", password="WrongPassword")
    assert e_info.value.status_code == 401

    with pytest.raises(VIRAError) as e_info:
        # Even with the correct environment variables set, parameters take precidence
        vira.connect(user="WrongUser", password=VIRA_TEST_USER_PASSWORD)
    assert e_info.value.status_code == 401

    with pytest.raises(VIRAError) as e_info:
        # Even with the correct environment variables set, parameters take precidence
        vira.connect_with_token(token="WrongPersonalAccessToken")
    assert e_info.value.status_code == 401
