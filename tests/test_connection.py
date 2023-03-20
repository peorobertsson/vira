from vira import VIRA
from vira import VIRAError
import pytest
import os
from tests.fixtures import VIRA_TEST_URL, VIRA_TEST_USER, VIRA_TEST_USER_PASSWORD


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_parameters(no_environment_variables_set):
    vira = VIRA()
    try:
        vira.connect(url=VIRA_TEST_URL, user=VIRA_TEST_USER,
                     password=VIRA_TEST_USER_PASSWORD)
    except VIRAError as e:
        exit(1)


@pytest.mark.usefixtures("correct_environment_variables_set")
def test_connection_with_environement_variables(correct_environment_variables_set):
    vira = VIRA()
    try:
        vira.connect()
    except VIRAError as e:
        exit(1)


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_with_console_input(no_environment_variables_set, monkeypatch):
    inputs = iter([VIRA_TEST_URL,
                  VIRA_TEST_USER, VIRA_TEST_USER_PASSWORD])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    vira = VIRA()
    try:
        vira.connect()
    except VIRAError as e:
        exit(1)


@pytest.mark.usefixtures("correct_environment_variables_set")
def test_failed_connection(correct_environment_variables_set):
    vira = VIRA()
    try:
        # Even with the correct environment variables set, parameters take precidence
        vira.connect(url=VIRA_TEST_URL, user="NonExistingUser",
                     password="WrongPassword")
    except VIRAError as e:  # Make sure exception is raised
        print(
            f"Error as expected. Message={e.message}, StatusCode={e.status_code}")
        assert (e.status_code == 401)
