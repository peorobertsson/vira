#!/usr/bin/env python3

# pip install jira
# import pip3 install python-dotenv

import logging
from logging.handlers import SysLogHandler
import sys

BOLD = '\033[1m'
RESET = '\033[0m'

DEFAULT_VIRA_URL = 'https://jira-vira.volvocars.biz'

# This goes to Per-Ola "PeO" Robertsson logging account
PAPERTRAIL_HOST = 'logs5.papertrailapp.com'
PAPERTRAIL_PORT = 14852


def getViraLoggerInit():
    logger = logging.getLogger('vira')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    try:
        pt_handler = SysLogHandler(
            address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))
        pt_handler.setFormatter(logging.Formatter(
            "%(levelname)-7s %(message)s"))
        pt_handler.setLevel(logging.INFO)
        logger.addHandler(pt_handler)
    except AttributeError as e:
        logger.error(
            f'Could not establish connection to {PAPERTRAIL_HOST}: {PAPERTRAIL_PORT}')

    logger.setLevel(logging.INFO)
    return logger


g_logger = getViraLoggerInit()


def getViraLogger():
    return g_logger
