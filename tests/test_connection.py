from vira import VIRA
from vira import VIRAError
import pytest
import os
from tests.fixtures import (
    VIRA_URL,
    VIRA_TEST_URL,
    VIRA_TEST_USER,
    VIRA_TEST_USER_PASSWORD,
    VIRA_TEST_ACCESS_TOKEN,
)


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_cridentials(no_environment_variables_set):
    vira = VIRA(VIRA_URL)
    vira.connect(user=VIRA_TEST_USER, password=VIRA_TEST_USER_PASSWORD)


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_token(no_environment_variables_set):
    vira = VIRA(VIRA_URL)
    vira.connect_with_token(token=VIRA_TEST_ACCESS_TOKEN)


@pytest.mark.usefixtures("correct_environment_variables_set")
def test_connection_with_cridentials_with_env_vars(correct_environment_variables_set):
    vira = VIRA(VIRA_URL)
    vira.connect()


@pytest.mark.usefixtures("correct_environment_variables_set")
def test_connection_with_token_using_env_vars(correct_environment_variables_set):
    vira = VIRA()
    vira.connect_with_token()


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_to_production(no_environment_variables_set):
    vira = VIRA(VIRA_URL)
    vira.connect(user=VIRA_TEST_USER, password=VIRA_TEST_USER_PASSWORD)


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_console_input(no_environment_variables_set, monkeypatch):
    inputs = iter([VIRA_TEST_USER, VIRA_TEST_USER_PASSWORD])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    vira = VIRA(VIRA_URL)
    vira.connect()


@pytest.mark.usefixtures("correct_environment_variables_set")
def test_failed_connection(correct_environment_variables_set):
    vira = VIRA(VIRA_TEST_URL)
    with pytest.raises(VIRAError) as e_info:
        # Even with the correct environment variables set, parameters take precidence
        vira.connect(user="NonExistingUser", password="WrongPassword")
    assert e_info.value.status_code == 401
