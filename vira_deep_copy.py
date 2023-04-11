#!/usr/bin/env python3

# pip install jira

from vira import VIRAError
from vira import VIRA
import argparse
import os.path
from script_utils import ask_for_confirmation, BOLD, RESET


# TODO(probert4): Test Support for Tasks (not just Stories)
# TODO(probert4): Also add links, i.e. keep the link structure in the copied structure. BIG WORK.
# TODO(probert4): Add script to delete (atleast add [DEPRECATED]) to a whole structure
# TODO(probert4): Make a seperate script to do shallow copy. (jira_copy)
# TODO(probert4): Make a seperate script to do rename strings in whole structure (vira_text_replace). Don't forget: When changing summary also change Feature Name of Features
# TODO(probert4): Make a seperate script to add/move parent (jira_add_parent)

# Notes
# Capability SOLSWEP-1201 .id=11500
#
# Capability SOLSWEP-1201 [Template, COPY ME] sSOLCSP Capability
#   Feature	ARTCSP-49118 [TEMPLATE, COPY ME] < capability > for < SM > [ND]
#   Feature	ARTCSP-49117 [TEMPLATE, COPY ME] < capability > [SA]
#   Feature	ARTCSP-49116[TEMPLATE, COPY ME] < capability > for < SM > [NT]
#   Feature	ARTCSP-49115 [TEMPLATE, COPY ME] < capability > for < SM > [DF]
#   Feature	ARTCSP-49114 [TEMPLATE, COPY ME] < capability > [ST]

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_AURTOUR = 'Per-Ola "PeO" Robertsson'
SCRIPT_VERSION = '0.3.0'

# Release notes
SCRIPT_RELEASE_NOTES = [
    [SCRIPT_VERSION, "2023-03-20", "Initial alpha release for feedback"],
    ["0.2.0", "2023-02-11", "Refactored to use VIRA module"],
    ["0.1.0", "2023-02-10", "First working version"],
]


def print_children(issue, indent_str: str = ''):
    children = issue.get_children()
    if len(children) > 0:
        print(f'{indent_str}{issue.short_str}, has {len(children)} children')
    else:
        print(f'{indent_str}{issue.short_str}')
    for child in children:
        print_children(child, indent_str + '  ')

    return indent_str[2:]  # Remove 2 spaces


def main(vira, *, src_issue_key: str, parent_issue_key: str = None):

    try:
        src_issue = vira.get_issue(src_issue_key)
    except VIRAError as e:
        print(
            f"Could not get issue {src_issue_key}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
        exit(1)

    parent_issue = None
    if parent_issue_key not in [None, '']:
        try:
            parent_issue = vira.get_issue(parent_issue_key)
        except VIRAError as e:
            print(
                f"Could not get issue {parent_issue_key}. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
            exit(1)

    # Parent (if provided) must be same issuetype as the source issue, check that we can add all sub-issue to the parent
    if parent_issue is not None:
        children = src_issue.get_children()
        if len(children) == 0:
            print(
                "Source issue has no children and parent_issue provided. Nothing will be copied. Aborting.")
            # Check that we can make copied sub-issues a parent
            # Don't have the child_issues yet, but use src_issue since it is has the same issue_type as the copy will have
            for child in children:
                can_be_child, error_str = vira.can_be_child_to_parent(
                    parent_issue=parent_issue, child_issue=src_issue_key)
                if not can_be_child:
                    print(f'{error_str}. Aborting.')
                    exit(1)

        print(
            f'Will deep copy child issues of {src_issue.short_str} and will add them as children to {parent_issue.short_str}')
    else:
        print(f'Will deep copy {src_issue.short_str}')

    replacements = vira.get_replacements()
    if len(replacements) > 0:
        print(f'Will use the following text replacements')
        for replacement in vira.get_replacements():
            print(f'"{replacement[0]}" -> "{replacement[1]}"')
    else:
        print(f'Will not do any text replacements')

    ask_for_confirmation()

    copy_issue = vira.copy_issue_recursive(
        src_issue, parent_issue=parent_issue)

    print("Summary:")
    if copy_issue is not None:
        print_children(copy_issue)
    else:
        print('No issues created')

    return


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
    parser.add_argument('-u', '--user',
                        help="Your VIRA user, i.e Your CDSID. If not provided you will be prompted to enter")
    parser.add_argument('-pw', '--password',
                        help="Your VIRA password. If not provided you will be prompted to enter")
    parser.add_argument('--vira_url', default='https://jira-vira.volvocars.biz',
                        help="VIRA URL. If not specified the standard VIRA URL will be used")

    # Parse the arguments
    g_args = parser.parse_args()

    replacements = [["[TEMPLATE, COPY ME] ", ""],
                    ["[Template, COPY ME] ", ""]]
    if g_args.capability_replace_text is not None:
        replacements.append(["<capability>", g_args.capability_replace_text])
        replacements.append(
            ["<sSOLCSP Capability>", g_args.capability_replace_text])
    if g_args.sm_replace_text is not None:
        replacements.append(["<SM>", g_args.sm_replace_text])

    vira = VIRA()

    # Connect to Jira
    try:
        vira.connect(url=g_args.vira_url, user=g_args.user,
                     password=g_args.password)
    except VIRAError as e:
        print(
            f"Could not connect to VIRA {g_args.vira_url}'. Aborting. Details:\n{e.status_code} {e.message}\n{e.jira_error.response.content}")
        exit(1)

    vira.set_replacements(replacements)
    vira.set_create_comment(
        f"This issue was created by {SCRIPT_NAME} {SCRIPT_VERSION}")

    main(vira, src_issue_key=g_args.src_issue,
         parent_issue_key=g_args.parent_issue)
