
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
