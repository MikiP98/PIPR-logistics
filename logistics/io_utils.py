_RED = "\033[91m"
_YELLOW = "\033[93m"

_ITALIC = "\033[3m"

_RESET = "\033[0m"


_FALSE_INPUT_VALUES = frozenset(('0', 'nie', 'no', 'n', 'false', 'f'))
_TRUE_INPUT_VALUES = frozenset(('1', 'tak', 'yes', 'y', 'true', 't'))
_BOOL_INPUT_VALUES = _FALSE_INPUT_VALUES.union(_TRUE_INPUT_VALUES)


def ask_for_bool(question: str) -> bool:
    user_input = ""
    while user_input not in _BOOL_INPUT_VALUES:
        print(question)
        user_input = get_input("y/n").lower()
        if user_input not in _BOOL_INPUT_VALUES:
            invalid_input()
    return user_input in _TRUE_INPUT_VALUES


def ask_for_string(question: str) -> str:
    print(question)
    return get_input()


# def ask_for_choice(question: str, options: list[str]) -> int:
#     """
#     Asks the user to select an option using arrow keys.
#     Styled to match the app's Cyan/Gray theme.
#     """
#
#     # 2. Define Custom Style to match your app
#     custom_style = Style([
#         ('title', 'fg:default'),
#         ('highlighted', 'fg:cyan italic'),
#         ('selected', 'fg:default'),
#     ])
#
#     # 3. Show Prompt
#     answer = questionary.select(
#         question,
#         choices=options,
#         style=custom_style,
#         pointer=">",           # Matches the symbol in get_input()
#         qmark=""               # Hides the default '?'
#     ).ask()
#
#     return options.index(answer)


def ask_for_choice(options: list[str], question: str = "What would you like to do?") -> int:
    def validade_input(user_input):
        return (
            user_input.lower() in options_lower
            or (user_input.isnumeric() and len(options) > int(user_input) > 0)
        )
    options_lower = [o.lower() for o in options]
    user_input = ""
    while not validade_input(user_input):
        print(question)
        for i, o in enumerate(options):
            print(f"{i}. {o}")
        print()
        user_input = get_input()
        if not validade_input(user_input):
            invalid_input()
    if user_input.lower() in options_lower:
        user_input = options_lower.index(user_input.lower())
    return user_input


def invalid_input() -> None:
    print(f"{_RED}Invalid input{_RESET}\n")


def get_input(tip: str = "") -> str:
    result = input(f"{_ITALIC}Enter your choice{f" ({tip})" if len(tip) > 0 else ''}: {_RESET}")
    return result


def log(msg: str) -> None:
    print(f"{msg}{_RESET}")


def warn(msg: str) -> None:
    print(f"{_YELLOW}{msg}{_RESET}")


def error(msg: str) -> None:
    print(f"{_RED}{msg}{_RESET}")


if __name__ == '__main__':
    # log("Testing...")
    # print()
    # print(ask_for_bool("Do you want me to do it?"))
    print()
    options = [
        "Change database path",
        "Change database filename",
        "Override the file (file will be permanently lost)",
        "Cancel database setup"
    ]
    selection = ask_for_choice(options)
