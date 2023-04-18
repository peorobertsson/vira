import argparse
BOLD = "\033[1m"
RESET = "\033[0m"


def ask_for_confirmation():
    while True:
        user_input = input("Do you want to continue? (yes/no) ")
        if user_input.lower() == "yes":
            break
        elif user_input.lower() == "no":
            exit(0)
        else:
            print("Please enter 'yes' or 'no'.")


def print_version(SCRIPT_NAME, SCRIPT_AUTHOUR, SCRIPT_VERSION, SCRIPT_RELEASE_NOTES):
    print(f'{SCRIPT_NAME} v{SCRIPT_VERSION} by {SCRIPT_AUTHOUR}')

    print('Release Notes')
    for release_note in SCRIPT_RELEASE_NOTES:
        print(f'{release_note[0]:<6} {release_note[1]:<10} {release_note[2]}')


def add_common_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('-u', '--user',
                        help="Your VIRA user, i.e Your CDSID. If not provided you will be prompted to enter")
    parser.add_argument('-pw', '--password',
                               help="Your VIRA password. If not provided you will be prompted to enter")
    parser.add_argument('-pat', '--token',
                        help="Your Personal Acccess Token. If not provided --user and --password will be used")
    parser.add_argument('--vira_url', default='https://jira-vira.volvocars.biz',
                        help="VIRA URL. If not specified the standard VIRA URL will be used")
