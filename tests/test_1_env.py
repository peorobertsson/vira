import os


def test_env_variables():
    # Will cause exception if environment variables are not set
    os.environ["VIRA_TEST_USER"]
    os.environ["VIRA_TEST_USER_PASSWORD"]
    os.environ["VIRA_TEST_ACCESS_TOKEN"]


if __name__ == "__main__":
    os.system("export")
    test_env_variables()
