import os
import pytest

from tests.cridentials import (
    VIRA_URL,
    VIRA_TEST_URL,
    VIRA_TEST_USER,
    VIRA_TEST_USER_PASSWORD,
    VIRA_TEST_ACCESS_TOKEN,
)

scripts_dir = os.path.dirname(__file__) + "/../src"


def test_vira_deep_copy():
    dirname = os.path.dirname(__file__)
    args = f"python3 {scripts_dir}/vira_deep_copy.py --vira_url {VIRA_TEST_URL} -pat {VIRA_TEST_ACCESS_TOKEN} --force ARTCSP-48111"
    exit_code = os.system(args)
    assert exit_code == 0


def test_vira_copy():
    dirname = os.path.dirname(__file__)
    args = f"python3 {scripts_dir}/vira_copy.py --vira_url {VIRA_TEST_URL} -pat {VIRA_TEST_ACCESS_TOKEN} --force ARTCSP-48111"
    exit_code = os.system(args)
    assert exit_code == 0


@pytest.mark.skip("Update script first")
def test_vira_add_parent():
    dirname = os.path.dirname(__file__)
    args = f"python3 {scripts_dir}/vira_add_parent.py --vira_url {VIRA_TEST_URL} -pat {VIRA_TEST_ACCESS_TOKEN} --force -s ARTCSP-48111 -p SOLSWEP-1293"
    exit_code = os.system(args)
    assert exit_code == 0
