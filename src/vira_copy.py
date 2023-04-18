#!/usr/bin/env python3

from vira import VIRAError
from vira import VIRA
import argparse
import os.path
import script_utils

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_AURTOUR = 'Per-Ola "PeO" Robertsson'
SCRIPT_VERSION = '0.9.0'

# Release notes
SCRIPT_RELEASE_NOTES = [
    [SCRIPT_VERSION, "2023-03-20", "Initla alpha release for feedback"],
]


def main(vira, *, src_issue_key: str, parent_issue_key: str = None):

    try:
        src_issue = vira.get_issue(src_issue_key)
    except VIRAError as e:
        print(
            f"Could not get issue {src_issue_key}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")  # TODO(probert4) add e.details
        exit(1)

    parent_issue = None
    if parent_issue_key not in [None, '']:
        try:
            parent_issue = vira.get_issue(parent_issue_key)
        except VIRAError as e:
            print(
                f"Could not get issue {parent_issue_key}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
            exit(1)

    # Check that we can make the copied issue a parent
    # Don't have the child_issue yet, but use src_issue since it is has the same issue_type aas the copy will have
    can_be_child, _ = vira.can_be_child_to_parent(
        parent_issue=parent_issue, child_issue=src_issue)
    if not can_be_child:
        print(
            f"Can't add a copy of {src_issue} as parent to {parent_issue}. Aborting.")
        exit(1)

    # Non recursive copy. Parent (if provided) must be one hirarcical level
    log_str = f'Will copy issue {src_issue.short_str}'
    if parent_issue is not None:
        log_str += f' and will add it as child to {parent_issue.short_str}'

    print(log_str)

    if not g_args.force:
        script_utils.ask_for_confirmation()

    copy_issue = vira.copy_issue(src_issue, parent_issue=parent_issue)

    print("Summary:")
    if copy_issue is not None:
        log_str = f'Created issue {copy_issue.short_str}'
        if parent_issue is not None:
            log_str += f' and made it a child to {parent_issue.short_str}'
        print(log_str)
    else:
        print('No issues created')

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f'{SCRIPT_NAME} {SCRIPT_VERSION}. Deep Copies a VIRA issue. Created by {SCRIPT_AURTOUR}.\nRelease notes:\n{SCRIPT_RELEASE_NOTES}')

    parser.add_argument('src_issue',
                        help="The issue to copy from")
    parser.add_argument('-p', '--parent_issue',
                        help="If specified the copy will be added to the parent. Need to be a one level up issuetype as the --src_issue aragument. If not specified the copy will not have a parent")

    script_utils.add_common_arguments(parser)

    # Parse the arguments
    g_args = parser.parse_args()

    vira = VIRA(g_args.vira_url)

    # Connect to Jira
    try:
        if g_args.token is not None:
            vira.connect_with_token(token=g_args.token)
        else:
            vira.connect(user=g_args.user, password=g_args.password)
    except VIRAError as e:
        print(
            f"Could not connect to VIRA {g_args.vira_url}'. Aborting. Details:\n{e.status_code} {e.message}")
        exit(1)

    vira.set_create_comment(
        f"This issue was created by {SCRIPT_NAME} {SCRIPT_VERSION}")

    main(vira, src_issue_key=g_args.src_issue,
         parent_issue_key=g_args.parent_issue)
