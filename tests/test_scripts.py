import sys
import pytest
from unittest.mock import patch

from tests.conftest import (
    VIRA_TEST_URL,
    VIRA_TEST_ACCESS_TOKEN,
)

import vira.vira_deep_copy as vira_deep_copy
import vira.vira_copy as vira_copy
import vira.vira_add_parent as vira_add_parent


def test_vira_deep_copy():
    args = [
        "vira_deep_copy",
        "--vira_url",
        VIRA_TEST_URL,
        "-pat",
        VIRA_TEST_ACCESS_TOKEN,
        "--force",
        "ARTCSP-48111",
    ]
    with patch.object(sys, "argv", args):
        vira_deep_copy.main()


def test_vira_deep_copy_failure():
    args = [
        "vira_deep_copy",
        "--vira_url",
        VIRA_TEST_URL,
        "-pat",
        VIRA_TEST_ACCESS_TOKEN,
        "--force",
        "NonExisting-48111",
    ]
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", args):
            vira_deep_copy.main()


def test_vira_copy():
    args = [
        "vira_copy",
        "--vira_url",
        VIRA_TEST_URL,
        "-pat",
        VIRA_TEST_ACCESS_TOKEN,
        "--force",
        "ARTCSP-48111",
    ]
    with patch.object(sys, "argv", args):
        vira_copy.main()


@pytest.mark.skip("Need updated script")
def test_vira_add_parent():
    args = [
        "vira_add_parent",
        "--vira_url",
        VIRA_TEST_URL,
        "-pat",
        VIRA_TEST_ACCESS_TOKEN,
        "--force",
        "ARTCSP-48111",
        "SOLSWEP-1293",
    ]
    with patch.object(sys, "argv", args):
        vira_add_parent.main()
