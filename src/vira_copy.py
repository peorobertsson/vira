#!/usr/bin/env python3

from vira import VIRAError
from vira import VIRA
import argparse
import os.path
import vira_script_utils

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_AURTOUR = 'Per-Ola "PeO" Robertsson'
SCRIPT_VERSION = "0.9.0"

# Release notes
SCRIPT_RELEASE_NOTES = [
    [SCRIPT_VERSION, "2023-03-20", "Initla alpha release for feedback"],
]


def main():
    parser = argparse.ArgumentParser(
        description=f"{SCRIPT_NAME} {SCRIPT_VERSION}. Deep Copies a VIRA issue. Created by {SCRIPT_AURTOUR}.\nRelease notes:\n{SCRIPT_RELEASE_NOTES}"
    )

    parser.add_argument("src_issue", help="The issue to copy from")
    parser.add_argument(
        "-p",
        "--parent_issue",
        help="If specified the copy will be added to the parent. Need to be a one level up issuetype as the --src_issue aragument. If not specified the copy will not have a parent",
    )

    vira_script_utils.add_common_arguments(parser)

    # Parse the arguments
    args = parser.parse_args()

    vira = VIRA(args.vira_url)

    # Connect to Jira
    try:
        if args.token is not None:
            vira.connect_with_token(token=args.token)
        else:
            vira.connect(user=args.user, password=args.password)
    except VIRAError as e:
        print(
            f"Could not connect to VIRA {args.vira_url}'. Aborting. Details:\n{e.status_code} {e.message}"
        )
        exit(1)

    vira.set_create_comment(f"This issue was created by {SCRIPT_NAME} {SCRIPT_VERSION}")

    try:
        src_issue = vira.get_issue(args.src_issue)
    except VIRAError as e:
        print(
            f"Could not get issue {args.src_issue}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}"
        )
        exit(1)

    parent_issue = None
    if args.parent_issue not in [None, ""]:
        try:
            parent_issue = vira.get_issue(args.parent_issue)
        except VIRAError as e:
            print(
                f"Could not get issue {args.parent_issue}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}"
            )
            exit(1)

    # Check that we can make the copied issue a parent
    # Don't have the child_issue yet, but use src_issue since it is has the same issue_type aas the copy will have
    can_be_child, _ = vira.can_be_child_to_parent(
        parent_issue=parent_issue, child_issue=src_issue
    )
    if not can_be_child:
        print(f"Can't add a copy of {src_issue} as parent to {parent_issue}. Aborting.")
        exit(1)

    # Non recursive copy. Parent (if provided) must be one hirarcical level
    log_str = f"Will copy issue {src_issue.short_str}"
    if parent_issue is not None:
        log_str += f" and will add it as child to {parent_issue.short_str}"

    print(log_str)

    if not args.force:
        vira_script_utils.ask_for_confirmation()

    copy_issue = vira.copy_issue(src_issue, parent_issue=parent_issue)

    print("Summary:")
    if copy_issue is not None:
        log_str = f"Created issue {copy_issue.short_str}"
        if parent_issue is not None:
            log_str += f" and made it a child to {parent_issue.short_str}"
        print(log_str)
    else:
        print("No issues created")

    return


if __name__ == "__main__":
    main()
