#!/usr/bin/env python3

from vira import VIRA
from vira import VIRAError
import argparse
import os.path
from script_utils import ask_for_confirmation, BOLD, RESET

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_AURTOUR = 'Per-Ola "PeO" Robertsson'
SCRIPT_VERSION = '0.1.0'

# Release notes
SCRIPT_RELEASE_NOTES = [
    [SCRIPT_VERSION, "2023-03-20", "Initial alpha release for feedback"],
]


def main(vira, *, issue_key: str, new_parent_issue_key: str):

    try:
        issue = vira.get_issue(issue_key)
    except VIRAError as e:
        print(
            f"Could not get issue {issue_key}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
        exit(1)

    new_parent_issue = None
    if new_parent_issue_key not in [None, '']:
        try:
            new_parent_issue = vira.get_issue(new_parent_issue_key)
        except VIRAError as e:
            print(
                f"Could not get issue {new_parent_issue_key}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
            exit(1)

    can_be_child, error_str = vira.can_be_child_to_parent(
        parent_issue=new_parent_issue, child_issue=issue_key)
    if not can_be_child:
        print(f'{error_str}. Aborting.')
        exit(1)

    print(f'Will make {issue.short_str} child of {new_parent_issue.short_str}')

    ask_for_confirmation()

    vira.add_child_issue_to_parent(parent_issue=new_parent_issue,
                                   child_issue=issue)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f'{SCRIPT_NAME} {SCRIPT_VERSION}. Deep Copies a VIRA issue. Created by {SCRIPT_AURTOUR}.\nRelease notes:\n{SCRIPT_RELEASE_NOTES}')

    parser.add_argument('-s', '--src_issue', required=True,
                        help="The issue to copy from")
    parser.add_argument('-p', '--parent_issue',
                        help="If specified only sub issues of --src_issue will be copied to this issue. Need to be of same VIRA issuetype as the --src_issue aragument. If not specified a complete deep copy of --src_issue will be done.")
    parser.add_argument('-c', '--capability_replace_text',
                        help="Replaces the <capability> string of the template issues with this text. Tip: Use the name of the capability")
    parser.add_argument('-sm', '--sm_replace_text',
                        help="Replaces the <SM> string of the template issues with this text. Tip: Use the name of a Specific Module (node) that is part of the capability. Example: HP, HI, EthSw, SGA, VIU")

    # Parse the arguments
    g_args = parser.parse_args()

    vira = VIRA()

    # Connect to Jira
    try:
        vira.connect(url=g_args.vira_url, user=g_args.user,
                     password=g_args.password)
    except VIRAError as e:
        print(
            f"Could not connect to VIRA {g_args.vira_url}'. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
        exit(1)

    main(vira, issue_key=g_args.src_issue,
         new_parent_issue_key=g_args.parent_issue)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f'{SCRIPT_NAME} {SCRIPT_VERSION}. Add or moves a VIRA issue to annother parent. Created by {SCRIPT_AURTOUR}')

    parser.add_argument('-d', '--issue', required=True,
                        help="The issue")
    parser.add_argument('--parent', required=True,
                        help="The new parent issue. The parent must be one hirarcical level up to the --issue")

    parser.add_argument('-u', '--user',
                        help="Your VIRA user, i.e Your CDSID. If not provided you will be prompted to enter")
    parser.add_argument('-pw', '--password',
                        help="Your VIRA password. If not provided you will be prompted to enter")
    parser.add_argument('--vira_url', default='https://jira-vira.volvocars.biz',
                        help="VIRA URL. If not specified the standard VIRA URL will be used")

    vira = VIRA()

    # Connect to Jira
    try:
        vira.connect(url=g_args.vira_url, user=g_args.user,
                     password=g_args.password)
    except VIRAError as e:
        print(
            f"Could not connect to VIRA {g_args.vira_url}'. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
        exit(1)

    main(vira, issue_key=g_args.issue,
         new_parent_issue_key=g_args.parent)
