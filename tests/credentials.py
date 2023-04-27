from dotenv import dotenv_values

test_credentials = dotenv_values(".env.test_credentials")

VIRA_URL = "https://jira-vira.volvocars.biz"  # Production environment
VIRA_TEST_URL = "https://jira-vira-qa.volvocars.biz"  # QA environment
VIRA_TEST_USER = test_credentials["VIRA_TEST_USER"]
VIRA_TEST_USER_PASSWORD = test_credentials["VIRA_TEST_USER_PASSWORD"]
VIRA_TEST_ACCESS_TOKEN = test_credentials["VIRA_TEST_ACCESS_TOKEN"]
