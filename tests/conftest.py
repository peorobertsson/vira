from dotenv import load_dotenv
import pytest
import os

import os
from dotenv import load_dotenv

load_dotenv()  # set environemnt variables from .env file (if it exists)

VIRA_URL = "https://jira-vira.volvocars.biz"  # Production environment
VIRA_TEST_URL = "https://jira-vira-qa.volvocars.biz"  # QA environment
VIRA_TEST_USER = os.environ["VIRA_TEST_USER"]
VIRA_TEST_USER_PASSWORD = os.environ["VIRA_TEST_USER_PASSWORD"]
VIRA_TEST_ACCESS_TOKEN = os.environ["VIRA_TEST_ACCESS_TOKEN"]


@pytest.fixture
def no_environment_variables_set():
    if "VIRA_USER" in os.environ:
        del os.environ["VIRA_USER"]
    if "VIRA_PASSWORD" in os.environ:
        del os.environ["VIRA_PASSWORD"]
    if "VIRA_ACCESS_TOKEN" in os.environ:
        del os.environ["VIRA_ACCESS_TOKEN"]


@pytest.fixture
def correct_test_environment_variables_set():
    os.environ["VIRA_URL"] = VIRA_TEST_URL
    os.environ["VIRA_USER"] = VIRA_TEST_USER  # type: ignore
    os.environ["VIRA_PASSWORD"] = VIRA_TEST_USER_PASSWORD  # type: ignore
    os.environ["VIRA_ACCESS_TOKEN"] = VIRA_TEST_ACCESS_TOKEN  # type: ignore
