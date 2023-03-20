#!/usr/bin/env python3

# pip install jira

from scripts.vira_deep_copy import add_child_issue_to_parent
from symbol import parameters
from jira import JIRA
from jira import JIRAError
import argparse
import logging
import os.path

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_VERSION = '0.1.0'
SCRIPT_AURTOUR = 'Per-Ola "PeO" Robertsson'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f'{SCRIPT_NAME} {SCRIPT_VERSION}. Add or moves a VIRA issue to annother parent. Created by {SCRIPT_AURTOUR}')

    parser.add_argument('-u', '--user', required=True,
                        help="Your VIRA user, i.e Your CDSID.")
    parser.add_argument('-p', '--password', required=True,
                        help="Your VIRA password")
    parser.add_argument('-d', '--issue', required=True,
                        help="The issue")
    parser.add_argument('--parent', required=True,
                        help="The new parent issue. The parent must be one hirarcical level up to the --issue")
    parser.add_argument(
        '--vira_url', default='https://jira-vira.volvocars.biz', help="VIRA URL")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Verbose output")

    # Parse the arguments
    g_args = parser.parse_args()

    logging_level = logging.INFO
    if (g_args.verbose):
        logging_level = logging.DEBUG

    logging.basicConfig(format='%(levelname)s:%(lineno)d:%(message)s',
                        level=logging_level)

    # Connect to Jira
    try:
        jira = JIRA(server=g_args.vira_url, auth=(
            g_args.user, g_args.password))
    except JIRAError as e:
        logger.error(
            f"Could not connect to JIRA {g_args.vira_url} as '{g_args.user}'. Aborting. Details:\n{e.response.status_code} {e.response.content}")
        exit(1)

    try:
        parent_issue = jira.issue(g_args.parent)
    except JIRAError as e:
        logger.error(
            f"Could not get issue {g_args.parent}. Aborting. Details:\n{e.response.status_code} {e.response.content}")
        exit(1)

    try:
        child_issue = jira.issue(g_args.child)
    except JIRAError as e:
        logger.error(
            f"Could not get issue {g_args.child}. Aborting. Details:\n{e.response.status_code} {e.response.content}")
        exit(1)

    add_child_issue_to_parent(jira, parent_issue=parent_issue,
                              child_issue=child_issue)
