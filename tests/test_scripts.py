import os
import pytest

from tests.credentials import (
    VIRA_TEST_URL,
    VIRA_TEST_ACCESS_TOKEN,
)


def test_vira_deep_copy():
    args = f"vira_deep_copy.py --vira_url {VIRA_TEST_URL} -pat {VIRA_TEST_ACCESS_TOKEN} --force ARTCSP-48111"
    exit_code = os.system(args)
    assert exit_code == 0


def test_vira_copy():
    args = f"vira_copy.py --vira_url {VIRA_TEST_URL} -pat {VIRA_TEST_ACCESS_TOKEN} --force ARTCSP-48111"
    exit_code = os.system(args)
    assert exit_code == 0


def test_vira_add_parent():
    args = f"vira_add_parent.py --vira_url {VIRA_TEST_URL} -pat {VIRA_TEST_ACCESS_TOKEN} --force ARTCSP-48111 SOLSWEP-1293"
    exit_code = os.system(args)
    assert exit_code == 0
