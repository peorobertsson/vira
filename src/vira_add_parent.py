#!/usr/bin/env python3

from vira import VIRA
from vira import VIRAError
import argparse
import os.path
import vira_script_utils

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_AURTOUR = 'Per-Ola "PeO" Robertsson'
SCRIPT_VERSION = "0.1.0"

# Release notes
SCRIPT_RELEASE_NOTES = [
    [SCRIPT_VERSION, "2023-03-20", "Initial alpha release for feedback"],
]


def main():
    parser = argparse.ArgumentParser(
        description=f"{SCRIPT_NAME} {SCRIPT_VERSION}. Add or moves a VIRA issue to annother parent. Created by {SCRIPT_AURTOUR}.\nRelease notes:\n{SCRIPT_RELEASE_NOTES}"
    )

    parser.add_argument("issue", help="The issue")
    parser.add_argument(
        "parent",
        help="The new parent issue. The parent must be one hirarcical level up to the --issue",
    )

    vira_script_utils.add_common_arguments(parser)

    # Parse the arguments
    args = parser.parse_args()

    vira = VIRA(args.vira_url)

    # Connect to Jira
    try:
        vira.connect(user=args.user, password=args.password)
    except VIRAError as e:
        print(
            f"Could not connect to VIRA {args.vira_url}'. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}"
        )
        exit(1)

    try:
        issue = vira.get_issue(args.issue)
    except VIRAError as e:
        print(
            f"Could not get issue {args.issue}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}"
        )
        exit(1)

    parent_issue = None
    if args.parent not in [None, ""]:
        try:
            parent_issue = vira.get_issue(args.parent)
        except VIRAError as e:
            print(
                f"Could not get issue {args.parent}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}"
            )
            exit(1)

    can_be_child, error_str = vira.can_be_child_to_parent(
        parent_issue=parent_issue, child_issue=issue
    )
    if not can_be_child:
        print(f"{error_str}. Aborting.")
        exit(1)

    print(f"Will make {issue.short_str} child of {parent_issue.short_str}")

    if not args.force:
        vira_script_utils.ask_for_confirmation()

    vira.add_child_issue_to_parent(parent_issue=parent_issue, child_issue=issue)


if __name__ == "__main__":
    main()
