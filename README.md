# volvo-jira
A python project to handle VIRA (Volvo Cars version of JIRA) issues.

Contains both a Python package (vira) and utility scripts.

Internal Volvo site with more info about how to use: https://confluence.volvocars.biz/display/ARTCSP/VIRA+Deep+Copy

![GitHubTestStatus](https://github.com/peorobertsson/vira/actions/workflows/tests.yml/badge.svg)

# For developers of volvo-jira

## tox envs
#### Linting
    tox -e mypy
    tox -e flake8
#### Run unit tests
    tox
#### Build package and publish with TWINE
    tox -e packaging
    twine upload dist/*
