from dotenv import load_dotenv
import pytest
import os

load_dotenv()  # set environemnt variables from .env file (if it exists)

VIRA_URL = "https://jira-vira.volvocars.biz"  # Production environment
VIRA_USER = os.getenv("VIRA_USER", "VIRA_USER_NOT_SET")
VIRA_USER_PASSWORD = os.getenv("VIRA_USER_PASSWORD", "VIRA_USER_PASSWORD_NOT_SET")
VIRA_ACCESS_TOKEN = os.getenv("VIRA_ACCESS_TOKEN", "VIRA_ACCESS_TOKEN_NOT_SET")

VIRA_TEST_URL = "https://jira-vira-qa.volvocars.biz"  # QA environment
VIRA_TEST_USER = os.getenv("VIRA_TEST_USER", "VIRA_TEST_USER_NOT_SET")
VIRA_TEST_USER_PASSWORD = os.getenv(
    "VIRA_TEST_USER_PASSWORD", "VIRA_TEST_USER_PASSWORD_NOT_SET"
)
VIRA_TEST_ACCESS_TOKEN = os.getenv(
    "VIRA_TEST_ACCESS_TOKEN", "VIRA_TEST_ACCESS_TOKEN_NOT_SET"
)


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
    os.environ["VIRA_USER"] = VIRA_TEST_USER
    os.environ["VIRA_PASSWORD"] = VIRA_TEST_USER_PASSWORD
    os.environ["VIRA_ACCESS_TOKEN"] = VIRA_TEST_ACCESS_TOKEN
