from vira import VIRA
import pytest

from tests.conftest import (
    VIRA_URL,
    VIRA_USER,
    VIRA_USER_PASSWORD,
    VIRA_ACCESS_TOKEN,
)


# Production VIRA tests
@pytest.mark.usefixtures()
def test_connection_to_production_with_cridentials():
    vira = VIRA(VIRA_URL)
    vira.connect(user=VIRA_USER, password=VIRA_USER_PASSWORD)


def test_connection_with_token():
    vira = VIRA(VIRA_URL)
    vira.connect_with_token(token=VIRA_ACCESS_TOKEN)


@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_to_production_using_console_input_pat(
    no_environment_variables_set, monkeypatch
):
    inputs = iter([VIRA_ACCESS_TOKEN])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    vira = VIRA(VIRA_URL)
    vira.connect_with_token()


@pytest.mark.skip("Fix this. monkeypatch can't emulate getpass.getpass() input.")
@pytest.mark.usefixtures("no_environment_variables_set")
def test_connection_to_production_using_console_input(
    no_environment_variables_set, monkeypatch
):
    inputs = iter([VIRA_USER, VIRA_USER_PASSWORD])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    vira = VIRA(VIRA_URL)
    vira.connect()
