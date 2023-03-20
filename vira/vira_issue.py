#!/usr/bin/env python3

# pip install jira

from jira import JIRA
from jira import JIRAError

from vira.vira_base import BOLD, RESET
from vira.vira_error import VIRAError
from vira.vira_base import getViraLogger

g_logger = getViraLogger()


class VIRAIssue:
    """Represents a single VIRA issue"""

    def __init__(self, jira_issue, jira):
        self._jira_issue = jira_issue
        self._jira = jira

    @ property
    def is_subtask(self) -> bool:
        return self.fields.issuetype.name == 'Sub-task'  # issuetype.id == 5

    @ property
    def is_story(self) -> bool:
        return self.fields.issuetype.name == 'Story'

    @ property
    def is_feature(self) -> bool:
        return self.fields.issuetype.name == 'Feature'

    @ property
    def is_capability(self) -> bool:
        return self.fields.issuetype.name == 'Capability'

    @ property
    def fields(self):
        return self._jira_issue.fields

    @ property
    def id(self) -> int:
        return self._jira_issue.id

    @ property
    def key(self) -> str:
        return self._jira_issue.key

    @ property
    def indent_str(self):
        if self.is_capability:
            return ''
        elif self.is_feature:
            return '  '
        elif self.is_story:
            return '    '
        elif self.is_subtask:
            return '      '
        else:
            g_logger.error(
                f'Unknown issue type {self.fields.issuetype.name}. Should never happen.')
            return ''

    def __repr__(self):
        return f'{self.key} {self.fields.issuetype.name}'

    def __str__(self):
        return f'{self.key} {self.fields.issuetype.name}'

    @ property
    def short_str(self):
        if self._jira_issue is None:
            return '<None>'
        return f'{BOLD}{self.fields.issuetype.name}{RESET} {self.key} "{self.fields.summary}"'

    @ property
    def children(self):
        """ Also gets the subtasks of Capabilities, Features, Stories and Tasks """

        children_issues = []
        if self.is_capability:
            # Get the children issues (Features) of the Capability
            children_issues = self._jira.search_issues(
                f'issueFunction in linkedIssuesOf("issue={self.key}", "is parent of") ORDER BY Rank')
        elif self.is_feature:
            # Get the the Stories/Tasks of the Feature
            children_issues = self._jira.search_issues(
                f'issueFunction in linkedIssuesOf("issue={self.key}", "is epic of") ORDER BY Rank')
        elif self.is_story:
            pass
        elif self.is_subtask:
            return []
        else:
            raise VIRAError(
                f"Can't get children of {self.short_str}. Unsupported issue type.")

        # Get the Subtasks of the Story/Task
        sub_task_issues = self._jira.search_issues(
            f'parent={self.key} ORDER BY Rank')

        # Convert from JIRAIssue to VIRAIssue object
        return_children = []
        for children_issue in children_issues:
            return_children.append(VIRAIssue(children_issue, self._jira))

        for sub_task_issue in sub_task_issues:
            return_children.append(VIRAIssue(sub_task_issue, self._jira))

        return return_children
