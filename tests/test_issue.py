from vira import VIRA
import pytest
import inspect
from tests.credentials import (
    VIRA_TEST_URL,
    VIRA_TEST_ACCESS_TOKEN,
)

VIRA_PROJECT_KEY = "ARTCSP"


@pytest.fixture
def vira(correct_test_environment_variables_set, scope="session"):
    vira = VIRA(VIRA_TEST_URL)
    vira.connect_with_token(token=VIRA_TEST_ACCESS_TOKEN)
    vira.set_create_comment("Created by unittest")
    return vira


@pytest.fixture
def src_capability_issue(vira, scope="session"):
    # SOLSWEP-802 - Capability: 'PRST gen I: Product Capability "Core System Platform State and Power Management"'
    issue = vira.get_issue("SOLSWEP-802")
    return issue


def test_get_issue(vira):
    # def get_issue(self, issue_key : str) -> VIRAIssue
    # ARTCSP-34668 - Feature: Test Feature 2'
    issue = vira.get_issue("ARTCSP-34668")

    assert issue.key == "ARTCSP-34668"
    assert issue.fields.summary == "Test Feature 2"
    assert issue.fields.status.name == "Done"
    assert len(issue.get_children()) == 12  # 12 - 11 Features and 1 Subtask


def calculate_n_children_recursive(issue, n_children=0):
    children = issue.get_children()
    print(f"{issue}, has {len(children)} children")
    n_children += len(children)
    for child in children:
        n_children = calculate_n_children_recursive(child, n_children)
    return n_children


def print_children(issue, indent_str: str = ""):
    children = issue.get_children()
    print(f"{indent_str}{issue}, has {len(children)} children")
    for child in children:
        print_children(child, indent_str + "  ")
    return indent_str[2:]  # Remove 2 spaces


def _function_name() -> str:
    return inspect.stack()[1][3]


def test_get_children(vira, src_capability_issue):
    children = src_capability_issue.get_children()
    assert len(children) == 3  # 3 - 1 Features and 2 SubTasks

    print_children(src_capability_issue)
    assert calculate_n_children_recursive(src_capability_issue) == 4


def test_create_issue(vira):
    # Some field must be set. Like project, issuetype and Summary. TODO(probert4) Add these as parameters in new create_issue_simple() method? That will also set 'Feature Name'
    fields = {
        "project": {"key": VIRA_PROJECT_KEY},
        "issuetype": "Story",
        "summary": "My own Story summary",
        "description": "My own Story description",
    }

    vira.set_create_comment("This issue was created by unit test test_create_issue")

    issue = vira.create_issue(fields)

    assert issue.fields.project.key == VIRA_PROJECT_KEY
    assert issue.fields.issuetype.name == "Story"
    assert issue.fields.summary == "My own Story summary"
    assert issue.fields.description == "My own Story description"

    # Depends on the workflow defined in the VIRA project what the default status should be
    assert issue.fields.status.name == "Open"

    assert issue.is_story


def test_copy_issue(vira):
    src_issue = vira.get_issue("SOLSWEP-803")
    vira.set_create_comment("This issue was created by unit test test_copy_issue")

    cpy_issue = vira.copy_issue(src_issue)

    assert cpy_issue.key != src_issue.key
    assert cpy_issue.id != src_issue.id
    assert cpy_issue.short_str != src_issue.short_str
    assert len(cpy_issue.get_children()) == 0
    assert cpy_issue.fields.project.key == src_issue.fields.project.key
    assert cpy_issue.fields.summary == src_issue.fields.summary
    assert cpy_issue.fields.description == src_issue.fields.description
    # TODO add more fileds test, status. Maybe even add a cmp overload to VIRAIssue?


def test_deep_copy(vira, src_capability_issue):
    vira.set_create_comment("This issue was created by unit test test_deep_copy")
    # def copy_issue_recursive(self, src_issue: VIRAIssue, *, copy_parent_issue: VIRAIssue = None) -> VIRAIssue:
    cpy_issue = vira.copy_issue_recursive(src_capability_issue)

    assert cpy_issue.is_capability

    assert cpy_issue.fields.summary == src_capability_issue.fields.summary
    assert cpy_issue.fields.description == src_capability_issue.fields.description
    # Depends on the workflow defined in the VIRA project what the default status should be
    assert cpy_issue.fields.status.name == "Funnel"

    assert calculate_n_children_recursive(cpy_issue) == calculate_n_children_recursive(
        src_capability_issue
    )


def test_deep_copy_to_parent(vira, src_capability_issue):
    parent_capability_issue = vira.copy_issue_by_key("SOLSWEP-803")
    vira.set_create_comment(
        "This issue was created by unit test test_deep_copy_to_parent"
    )
    parent_n_children_before = calculate_n_children_recursive(parent_capability_issue)

    cpy_issue = vira.copy_issue_recursive(
        src_capability_issue, copy_parent_issue=parent_capability_issue
    )

    assert cpy_issue == parent_capability_issue  # should return the parent issue

    assert calculate_n_children_recursive(
        cpy_issue
    ) - parent_n_children_before == calculate_n_children_recursive(src_capability_issue)
