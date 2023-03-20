from dotenv import dotenv_values
from vira import VIRAError
from vira import VIRA
import pytest
import os

test_cridentials = dotenv_values('.env.test_cridentials')

VIRA_TEST_URL = "https://jira-vira-qa.volvocars.biz"  # QA environment
VIRA_TEST_USER = test_cridentials['VIRA_TEST_USER']
VIRA_TEST_USER_PASSWORD = test_cridentials['VIRA_TEST_USER_PASSWORD']

@pytest.fixture
def no_environment_variables_set():
    if 'VIRA_URL' in os.environ:
        del os.environ['VIRA_URL']
    if 'VIRA_USER' in os.environ:
        del os.environ['VIRA_USER']
    if 'VIRA_PASSWORD' in os.environ:
        del os.environ['VIRA_PASSWORD']


@pytest.fixture
def correct_environment_variables_set():
    os.environ['VIRA_URL'] = VIRA_TEST_URL
    os.environ['VIRA_USER'] = VIRA_TEST_USER
    os.environ['VIRA_PASSWORD'] = VIRA_TEST_USER_PASSWORD
