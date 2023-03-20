from vira import VIRA
import pytest

VIRA_PROJECT_KEY = 'ARTCSP'


@pytest.mark.usefixtures("correct_environment_variables_set")
@pytest.fixture
def vira(correct_environment_variables_set):
    vira = VIRA()
    vira.connect()
    return vira


@pytest.fixture
def feature_issue(vira):
    # ARTCSP-34668 - Feature: 'Test Feature 2'
    issue = vira.get_issue('ARTCSP-34668')
    return issue


@pytest.fixture
def src_capability_issue(vira):
    # SOLSWEP-802 - Capability: 'PRST gen I: Product Capability "Core System Platform State and Power Management"'
    issue = vira.get_issue('SOLSWEP-802')
    return issue


@pytest.fixture
def parent_capability_issue(vira):
    # SOLSWEP-615 - Capability: 'TSC gen I: Product Capability "Provide Core System Application Execution"'
    issue = vira.get_issue('SOLSWEP-615')
    return issue


def test_get_issue(vira):
    # def get_issue(self, issue_key : str) -> VIRAIssue
    # ARTCSP-34668 - Feature: Test Feature 2'
    issue = vira.get_issue('ARTCSP-34668')

    assert issue.key == 'ARTCSP-34668'
    assert issue.fields.summary == 'Test Feature 2'
    assert len(issue.children) == 7 # 7 - 6 Features and 1 Subtask

    # SOLSWEP-802 - Capability: 'PRST gen I: Product Capability "Core System Platform State and Power Management"'
    # Has Sub-Tasks and Features
    issue = vira.get_issue('SOLSWEP-802')

    assert issue.key == 'SOLSWEP-802'
    assert issue.fields.summary == 'PRST gen I: Product Capability "Core System Platform State and Power Management"'
    assert len(issue.children) == 9  # 9 - 7 Features and 2 Subtasks


def calculate_n_children_recursive(issue, n_children=0):
    children = issue.children
 #   print(f'{issue}, has {len(children)} children')
    n_children += len(children)
    for child in issue.children:
        n_children = calculate_n_children_recursive(child, n_children)
    return n_children


def test_children(vira, src_capability_issue):
    def print_children(issue, indent_str: str):
        children = issue.children
        print(f'{indent_str}{issue}, has {len(children)} children')
        for child in children:
            print_children(child, indent_str + '  ')

        return indent_str[2:]  # Remove 2 spaces

    children = src_capability_issue.children
    assert len(children) == 9  # 9 - 7 Features and 2 SubTasks

    print_children(src_capability_issue, "")
    assert calculate_n_children_recursive(src_capability_issue) == 49


def test_create_issue(vira):
    # Some field must be set. Like project, issuetype and Summary. TODO(probert4) Add these as parameters in new create_issue_simple() method? That will also set 'Feature Name'
    fields = {'project': {'key': VIRA_PROJECT_KEY}, 'issuetype': 'Story',
              'summary': 'My own Story summary', 'description': 'My own Story description'}

    vira.set_create_comment(f'This issue was created by unit test {__name__}')

    issue = vira.create_issue(fields)

    assert issue.fields.project.key == VIRA_PROJECT_KEY
    assert issue.fields.issuetype.name == 'Story'
    assert issue.fields.summary == 'My own Story summary'
    assert issue.fields.description == 'My own Story description'

    # Depends on the workflow defined in the VIRA project what the default status should be
    assert issue.fields.status.name == 'Open'

    assert issue.is_story


def test_deep_copy(vira, src_capability_issue):

    vira.set_create_comment(f'This issue was created by unit test {__name__}')
    # def copy_issue_recursive(self, src_issue: VIRAIssue, *, copy_parent_issue: VIRAIssue = None) -> VIRAIssue:
    cpy_issue = vira.copy_issue_recursive(src_capability_issue)

    assert cpy_issue.is_capability

    assert cpy_issue.fields.summary == src_capability_issue.fields.summary
    assert cpy_issue.fields.description == src_capability_issue.fields.description
    # Depends on the workflow defined in the VIRA project what the default status should be
    assert cpy_issue.fields.status.name == 'Funnel'

    assert calculate_n_children_recursive(
        cpy_issue) == calculate_n_children_recursive(src_capability_issue)


def test_deep_copy_to_parent(vira, src_capability_issue, parent_capability_issue):

    parent_n_children_before = calculate_n_children_recursive(
        parent_capability_issue)

    cpy_issue = vira.copy_issue_recursive(
        src_capability_issue, copy_parent_issue=parent_capability_issue)

    assert cpy_issue == parent_capability_issue  # should return the parent issue

    assert calculate_n_children_recursive(
        cpy_issue) - parent_n_children_before == calculate_n_children_recursive(src_capability_issue)
