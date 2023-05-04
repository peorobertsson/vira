from jira import JIRA
from jira import JIRAError
from vira.vira_base import getViraLogger, get_os_identifier
from vira.vira_issue import VIRAIssue
from vira.vira_error import VIRAError
import os

# FIXME(probert4) Copy 'Status' Maybe status can be set after creation?
# TODO(probert4) Copy 'fixVersions' Maybe fixVersions can be set after creation
# TODO(probert4) Copy 'Remaing Estimate' and 'Original Estimate'.

g_logger = getViraLogger()


class VIRA:
    """Represent a VIRA instance."""

    def __init__(self, vira_url: str = None):
        """If vira_url is not provided, the VIRA_URL environment variable is used."""
        self._jira = None
        if vira_url is None:
            vira_url = os.environ.get("VIRA_URL")
        assert vira_url is not None
        self.vira_url = vira_url
        self.dry_run = False
        self.create_comment = None
        self.replacements = None

    def connect_with_token(self, *, token: str = None):
        # Connects to Jira/Vira using Personal Authentication Token (PAT)
        """If token is not provided, the VIRA_ACCESS_TOKEN environment variable is used."""
        if token is None:
            token = os.environ.get("VIRA_ACCESS_TOKEN")
        try:
            self._jira = JIRA(server=self.vira_url, token_auth=token)
        except JIRAError as e:
            raise VIRAError(
                f'Could not connect to VIRA server "{self.vira_url}" using Personal Authentication Token.',
                status_code=e.status_code,
                jira_error=e,
            )

        # To test that the authentication work, do some communication with the server. Done by doing a search
        try:
            self._jira.search_issues("issue=ANYTHNG")
        except JIRAError as e:
            # 400 is OK since the search was invalid, but the authentication was OK
            if e.status_code == 400:
                ...
            else:
                raise VIRAError(
                    f'Could not connect to VIRA server "{self.vira_url}" using Personal Authentication Token.',
                    status_code=e.status_code,
                    jira_error=e,
                )

        g_logger.info(
            f"Connected to {self.vira_url} using PAT. OS:{get_os_identifier()}"
        )

    def connect(self, *, user: str = None, password: str = None):
        """If a parameter is not provided, the corresponding OS environment variable is used. If these are not found the user is prompted to enter the
        URL and credentials.
        After a sucessfull connection, the values are stored as OS environemnt variables. Next call will then not need to specify a URL and credentials

        VIRA_USER,
        VIRA_PASSWORD
        """
        if user is None:
            user = os.environ.get("VIRA_USER")
        if password is None:
            password = os.environ.get("VIRA_PASSWORD")
        if user is None:
            user = input("Please enter your VIRA username:")
        if password is None:
            password = input("Please enter your VIRA password:")

        # Connects to Jira/Vira
        try:
            self._jira = JIRA(server=self.vira_url, auth=(user, password))
        except JIRAError as e:
            raise VIRAError(
                f'Could not connect to VIRA server "{self.vira_url}" as "{user}".',
                status_code=e.status_code,
                jira_error=e,
            )

        # Save for next time. TODO: Save this in a separate file
        os.environ["VIRA_USER"] = user
        os.environ["VIRA_PASSWORD"] = password

        g_logger.info(
            f"Connected to {self.vira_url} as {user}. OS:{get_os_identifier()}"
        )

    def get_issue(self, issue_key: str):
        try:
            jira_issue = self._jira.issue(issue_key)
        except JIRAError as e:
            raise VIRAError(
                f"Could not get VIRA issue with key '{issue_key}'. Status code {e.response.status_code}",
                status_code=e.response.status_code,
                jira_error=e,
            )

        return VIRAIssue(jira_issue, self._jira)

    def set_replacements(self, replacements):
        self.replacements = replacements

    def get_replacements(self):
        return self.replacements

    def replace_strings(self, src_str: str):
        if self.replacements is None:
            return src_str

        for matching, replacement in self.replacements:
            src_str = src_str.replace(matching, replacement)
        return src_str

    def can_be_child_to_parent(
        self, *, parent_issue: VIRAIssue, child_issue: VIRAIssue
    ):
        if parent_issue is None:
            return (True, "")

        if child_issue.is_feature:
            if not parent_issue.is_capability:
                return (
                    False,
                    f"Can only add a feature to a capability. Got parent issue {parent_issue} and child issue {child_issue}",
                )
            else:
                return (True, "")
        elif child_issue.is_story:
            if not parent_issue.is_feature:
                return (
                    False,
                    f"Can only add a Story to a Feature. Got parent issue {parent_issue} and child issue {child_issue}",
                )
            else:
                return (True, "")
        elif child_issue.is_subtask:
            if (
                parent_issue.is_subtask
            ):  # Subtasks can be made child of all issue types except subtasks
                return (
                    False,
                    f"Can not add a sub-task to a sub-task. Got parent issue {parent_issue} and child issue {child_issue}",
                )
            else:
                return (True, "")
        else:
            return (
                False,
                f"Can not add {child_issue.short_str} to {parent_issue.short_str}",
            )

    def add_child_issue_to_parent(
        self, *, parent_issue: VIRAIssue, child_issue: VIRAIssue
    ):
        can_be_child, error_str = self.can_be_child_to_parent(
            parent_issue=parent_issue, child_issue=child_issue
        )
        if not can_be_child:
            raise VIRAError(error_str)

        if child_issue.is_feature:
            assert (
                parent_issue.is_capability
            ), f"Can only add a feature to a capability. Got parent issue {parent_issue} and child issue {child_issue}"

            issue_dict = {
                # customfield_13801 = Capability Name. Example 'SOLSWEP-1201'
                "customfield_13801": parent_issue.key,
                # customfield_16500 = Capability ID. Example '3467866' (.id of SOLSWEP-1201)
                #            'customfield_16500': parent_issue.id
                "parent": {"id": parent_issue.id},
            }
            child_issue._jira_issue.update(fields=issue_dict)
        elif child_issue.is_story:
            assert (
                parent_issue.is_feature
            ), f"Can only add a Story to a Feature. Got parent issue {parent_issue} and child issue {child_issue}"

            # PROBERT4: Working for now, but with updated VIRA/JIRA this might stop working.
            # As of January 2022, add_issues_to_epic is not supported for next-gen projects
            # (you'll get this error: "Jira Agile Public API does not support this request").
            # https://ecosystem.atlassian.net/browse/ACJIRA-1634 explains how to do it now

            self._jira.add_issues_to_epic(
                parent_issue._jira_issue.id, child_issue._jira_issue.key
            )
        elif child_issue.is_subtask:
            assert (
                not parent_issue.is_subtask
            ), f"Can not add a sub-task to a sub-task. Got parent issue {parent_issue} and child issue {child_issue}"
            child_issue._jira_issue.update(fields={"parent": {"id": parent_issue.id}})
        else:
            raise VIRAError(
                f"Could not add {child_issue.short_str} to {parent_issue.short_str}"
            )

    def convert_field_value(self, src_field, src_field_value):
        dst_field_value = None

        if src_field_value is None:
            return None
        elif isinstance(src_field_value, (str, int)):
            return src_field_value
        elif type(src_field_value) == list:
            if len(src_field_value) == 0:
                return None
            # Remove list of one string or int. i.e ['string'] -> 'string' and [4] -> 4
            # BUT not for 'labels', labels needs to a an array of strings
            elif (
                len(src_field_value) == 1
                and isinstance(src_field_value[0], (str, int))
                and src_field != "labels"
            ):
                return src_field_value[0]
            else:
                dst_field_value = []
                for list_value in src_field_value:
                    dst_field_value.append(
                        self.convert_field_value(src_field, list_value)
                    )
        elif type(src_field_value).__name__ == "Version":
            dst_field_value = {"id": src_field_value.id}
        elif type(src_field_value).__name__ == "CustomFieldOption":
            dst_field_value = {"id": src_field_value.id}
        elif type(src_field_value).__name__ == "Priority":
            dst_field_value = {"name": src_field_value.name}
        elif type(src_field_value).__name__ == "User":
            dst_field_value = {"name": src_field_value.name}
        elif type(src_field_value).__name__ == "Status":
            dst_field_value = {"id": src_field_value.id}
        elif type(src_field_value).__name__ == "PropertyHolder":
            # TODO(probert4): Skip for now. 'progress', 'worklog', 'comment' fields. But maybe copy later?
            return None
        elif type(src_field_value).__name__ == "IssueType":
            dst_field_value = {"id": src_field_value.id}
        elif type(src_field_value).__name__ == "Project":
            dst_field_value = {"key": src_field_value.key}
        elif type(src_field_value).__name__ == "Watchers":
            return None  # Skip
        elif type(src_field_value).__name__ == "TimeTracking":
            return None  # Skip
        elif type(src_field_value).__name__ == "SecurityLevel":
            dst_field_value = {"id": src_field_value.id}
        elif type(src_field_value).__name__ == "Resolution":
            dst_field_value = {"name": src_field_value.name}
        elif type(src_field_value).__name__ == "Issue":
            dst_field_value = {"id": src_field_value.id}
        else:
            g_logger.warning(f"Unhandled type: {type(src_field_value)}")
            dst_field_value = src_field_value

        return dst_field_value

    def set_dry_run(self, dry_run=True):
        self.dry_run = dry_run

    def set_create_comment(self, comment):
        self.create_comment = comment

    def create_issue(self, issue_dict: dict):
        if not self.dry_run:
            try:
                new_jira_issue = self._jira.create_issue(fields=issue_dict)
            except JIRAError as e:
                g_logger.error(
                    f"Could not create issue. Details:\n{e.response.status_code} {e.response.content}",
                    extra={"no_console": True},
                )
                raise VIRAError(
                    "Could not create issue",
                    status_code=e.response.status_code,
                    jira_error=e,
                )
            if self.create_comment is not None:
                self._jira.add_comment(new_jira_issue, self.create_comment)
            new_issue = VIRAIssue(new_jira_issue, self._jira)
            g_logger.debug(f"Created issue {new_issue.short_str}")
            return new_issue
        g_logger.debug(f"Simulated the creation of issue {issue_dict}")
        return None

    def copy_issue_by_key(self, src_issue_key: str, *, parent_issue_key: str = None):
        src_issue = self.get_issue(src_issue_key)
        parent_issue = None
        if parent_issue_key is not None:
            parent_issue = self.get_issue(parent_issue_key)

        return self.copy_issue(src_issue=src_issue, parent_issue=parent_issue)

    def copy_issue(
        self, src_issue: VIRAIssue, *, parent_issue: VIRAIssue = None
    ) -> VIRAIssue:
        """Copies a single issue from another. If parent_issue is supplied it will make the copy a child of the parent issue.
        parent_issue must be one hirarcial level up of src_issue."""

        # Check that this is possible so that it will not fail after we made the copy (that can't be undone)
        can_be_child, error_str = self.can_be_child_to_parent(
            child_issue=src_issue, parent_issue=parent_issue
        )
        if not can_be_child:
            raise VIRAError(error_str)

        dst_summary = self.replace_strings(src_issue.fields.summary)

        if self.dry_run:
            log_str = f'Dry run: Would have copied {src_issue.indent_str}{src_issue.short_str} but changed the summary to "{dst_summary}"'
            if parent_issue is not None:
                log_str += f" and added it as child to {parent_issue.short_str}"
            g_logger.debug(log_str, extra={"console_only": True})
            return None

        # TODO(probert4) Check these
        read_only_fields = [
            "lastViewed",
            "creator",
            "customfield_15100",
            "subtasks",
            "created",
            "timeoriginalestimate",
            "customfield_14301",
            "customfield_16500",
            "customfield_16301",
            "customfield_15822",
            "customfield_13304",
            "customfield_10700",
            # customfield_15002 - Example: ['ART Core System Platform']
            "customfield_15002",
            "security",  # Read Only
            "aggregatetimeoriginalestimate",
            "timeestimate",
            "aggregatetimeestimate",
            "customfield_12803",
            "customfield_10703",
            "customfield_10705",
            "customfield_11103",
            "workratio",
            "issuelinks",
            # resolution can't be set when creating an issue. Can't create a done issue.
            "resolution",
            "resolutiondate",
            "updated",  # Can't be set when creating an issue
            "parent",  # Don't copy the parent, the copy issue will have annother parent
            # TODO(probert4) Maybe status can be set after creation?
            "status",
            # TODO(probert4) Maybe fixVersions can be set after creation
            "fixVersions",
        ]

        src_fields = src_issue.fields.__dict__.copy()

        # Remove read-only fields
        for field in read_only_fields:
            if field in src_fields:
                del src_fields[field]

        # Convert fields from JIRA Objects to values. Needed since JIRA Objects can't be JSON serialized by JIRA.create_issue()
        # Also remove the fields that are None
        dst_fields = {}
        for src_field, src_field_value in src_fields.items():
            # print(f'Src: {src_field}: {src_field_value}, {type(src_field_value)}')
            dst_field_value = self.convert_field_value(src_field, src_field_value)
            if dst_field_value is None:
                continue
            # print(f'Dst: {src_field}: {dst_field_value}, {type(dst_field_value)}')
            dst_fields[src_field] = dst_field_value

        # Replace the summary
        dst_fields["summary"] = dst_summary
        if src_issue.is_feature:
            # customfield_10704 - Feature Name. Set to same as summary.
            dst_fields["customfield_10704"] = dst_summary

        # parent must be set for a subtask when creating it
        if src_issue.is_subtask:
            if parent_issue is not None:
                dst_fields["parent"] = {"key": parent_issue.key}
            else:
                raise VIRAError("Parent must be set for a subtask when creating")
            if "reporter" in dst_fields:
                # reporter can't be set for a subtask when creating
                del dst_fields["reporter"]
            if "customfield_13802" in dst_fields:
                # customfield_13802 - Target Start (atleast for Sub-tasks it can't be set during creation)
                del dst_fields["customfield_13802"]

            if "customfield_13803" in dst_fields:
                # customfield_13803 - Target End (atleast for Sub-tasks it can't be set during creation)
                del dst_fields["customfield_13803"]

        new_issue = self.create_issue(dst_fields)

        # Set the parent issue
        if parent_issue is not None:
            self.add_child_issue_to_parent(
                parent_issue=parent_issue, child_issue=new_issue
            )

        log_string = f"Copied {src_issue.indent_str}{src_issue.short_str} to {new_issue.short_str}"

        if parent_issue is not None:
            log_string += f" and made it child to {parent_issue.short_str}"
        g_logger.info(log_string)

        return new_issue

    def copy_issue_recursive(
        self, src_issue: VIRAIssue, *, copy_parent_issue: VIRAIssue = None
    ) -> VIRAIssue:
        """Makes a deep copy of src_issue. If copy_parent_issue is provided then only sub-issues are copied and added to the copy_parent_issue.
        Will return the top parent of the copy. i.e. will return copy_parent_issue if not None.
        """

        if copy_parent_issue is None:
            copy_parent_issue = self.copy_issue(src_issue, parent_issue=None)
        else:
            if (
                src_issue.fields.issuetype.name
                != copy_parent_issue.fields.issuetype.name
            ):
                raise VIRAError(
                    f"Both source issue {src_issue.short_str} and parent issue {copy_parent_issue.short_str} must be of the same type"
                )

            if src_issue.key == copy_parent_issue.key:
                raise VIRAError(
                    f"Can't add children of same issue. Both source issue and parent issue {copy_parent_issue.short_str} is the same issue"
                )

        def copy_children(src_issue, copy_parent_issue):
            children = src_issue.get_children()
            for child in children:
                copy_child_issue = self.copy_issue(
                    child, parent_issue=copy_parent_issue
                )
                # The created issue will be parent to next child copy
                copy_children(child, copy_parent_issue=copy_child_issue)

        copy_children(src_issue, copy_parent_issue=copy_parent_issue)

        return copy_parent_issue
