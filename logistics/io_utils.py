from collections.abc import Sequence
from typing import Any

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
        user_input = get_input(tip="y/n").lower()
        if user_input not in _BOOL_INPUT_VALUES:
            invalid_input()
    return user_input in _TRUE_INPUT_VALUES


def ask_for_string(question: str) -> str:
    print(question)
    return get_input()


def ask_for_int(
        question: str, *, minimum: int | None = 0, maximum: int | None = 2**63-1, allow_none: bool = False
) -> int | None:
    if minimum is not None and maximum is not None and minimum >= maximum:
        raise ValueError("minimum has to be smaller than maximum")

    def validate_input(value: str) -> bool:
        return (
                (value.isnumeric()
                and (minimum is None or (minimum is not None and int(value) >= minimum))
                and (maximum is None or (maximum is not None and int(value) <= maximum)))
                or (allow_none and value == "")
        )

    user_input = ""
    while not validate_input(user_input):
        print(question)
        user_input = get_input().strip().replace(' ', '').replace(' ', '').replace('_', '')
        if not user_input.isnumeric():
            invalid_input()
        elif maximum is not None and int(user_input) > maximum:
            error(f"Exceeded max INTEGER size limit of '{maximum}'")
        elif minimum is not None and int(user_input) < minimum:
            error(f"Exceeded min INTEGER size limit of '{minimum}'")

    if user_input == "":
        return None
    else:
        return int(user_input)


def ask_for_float(question: str, *, minimum: float | None = 0, maximum: float | None = None) -> float:
    if minimum is not None and maximum is not None and minimum >= maximum:
        raise ValueError("minimum has to be smaller than maximum")

    def validate_input(value: str) -> bool:
        return (
            value.replace('.', '').replace(',', '').isnumeric()
            and (minimum is None or (minimum is not None and float(value) >= minimum))
            and (maximum is None or (maximum is not None and float(value) <= maximum))
        )

    user_input = ""
    while not validate_input(user_input):
        print(question)
        user_input = get_input().strip().replace(' ', '').replace(' ', '').replace('_', '')
        if not validate_input(user_input):
            invalid_input()
            # TODO: Improve the user feedback
    return float(user_input)


def ask_for_time(question: str) -> tuple[int, int, int, int, int]:
    # format -> ww:dd:hh:mm:ss

    def validate_input(value: str) -> bool:
        parts = value.split(':')
        return len(parts) <= 5 and all(part.isnumeric() for part in parts)

    user_input = ""
    while not validate_input(user_input):
        print(question)
        user_input = get_input(tip="ww:dd:hh:mm:ss").strip().replace(' ', '').replace(' ', '').replace('_', '')
        if not validate_input(user_input):
            invalid_input()
            # TODO: Improve the user feedback

    parts = user_input.split(':')
    offset = 5 - len(parts)
    weeks = int(parts[0]) if len(parts) == 5 else 0
    days = int(parts[1 - offset]) if len(parts) >= 4 else 0
    hours = int(parts[2 - offset]) if len(parts) >= 3 else 0
    minutes = int(parts[3 - offset]) if len(parts) >= 2 else 0
    seconds = int(parts[4 - offset])

    if seconds // 60 != 0:
        minutes += seconds // 60
        seconds %= 60

    if minutes // 60 != 0:
        hours += minutes // 60
        minutes %= 60

    if hours // 24 != 0:
        days += hours // 24
        hours %= 24

    if days // 7 != 0:
        weeks += days // 7
        days %= 7

    return weeks, days, hours, minutes, seconds


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


def ask_for_choice(
        options: list[str] | list[list[str]],
        question: str = "What would you like to do?",
        *,
        headers: bool = False
) -> int:
    if not options:
        raise ValueError("You must provide at least one option.")  # TODO: Make custom error

    # Check type of first element to decide strategy
    if isinstance(options[0], list):
        return _ask_column_choice(options, question, headers)
    else:
        return _ask_simple_choice(options, question, headers)


def _ask_simple_choice(options: list[str], question: str, headers: bool) -> int:
    header = None
    if headers:
        header = options.pop(0)
    valid_options = [o for o in options if o is not None]
    options_lower = [o.lower() for o in valid_options]

    def validate_input(value: str) -> bool:
        # Allow string match OR numeric index within bounds
        if value.lower() in options_lower:
            return True
        if value.isnumeric():
            idx = int(value)
            return 0 <= idx < len(options)
        return False

    user_input = ""
    while not validate_input(user_input):
        print(question)
        if header is not None:
            print(header)
            print('-'*max([len(o) for o in options if o is not None]))
        i = 0
        for o in options:
            if o is not None:
                print(f"{i}. {o}")
                i += 1
            else:
                print()
        print()

        user_input = get_input()
        if not validate_input(user_input):
            invalid_input()

    # Return index
    if user_input.isnumeric():
        return int(user_input)
    return options_lower.index(user_input.lower())


def _ask_column_choice(option_groups: list[list[str]], question: str, use_headers: bool) -> int:
    divider: str = "|"
    padding: int = 2

    if use_headers:
        # Take the first element of each list as header
        # Treat None as empty string for header
        headers = [str(col[0]).upper() if col and col[0] is not None else "" for col in option_groups]
        # Data is everything after the first element
        data_groups = [col[1:] if len(col) > 1 else [] for col in option_groups]
    else:
        headers = []
        data_groups = option_groups

    # Flatten the list for easy validation and index lookup
    flat_valid_options = [item for sublist in data_groups for item in sublist if item is not None]
    flat_valid_options_lower = [o.lower() for o in flat_valid_options]

    def validate_input(user_input: str) -> bool:
        if user_input.lower() in flat_valid_options_lower:
            return True
        if user_input.isnumeric():
            idx = int(user_input)
            return 0 <= idx < len(flat_valid_options)
        return False

    # 3. Pre-calculate the display strings for Data
    display_grid = []
    current_idx = 0
    for col in data_groups:
        display_col = []
        for item in col:
            if item is None:
                display_col.append("")
            else:
                display_col.append(f"{current_idx}. {item}")
                current_idx += 1
        display_grid.append(display_col)

    # 4. Calculate Column Widths (Must fit Header AND longest Data Item)
    col_widths = []
    for i in range(len(option_groups)):
        # Width of data items in this column
        data_col = display_grid[i]
        max_data_w = max(len(s) for s in data_col) if data_col else 0

        # Width of header (if exists)
        header_w = len(headers[i]) if use_headers else 0

        # Final width is the max of both
        col_widths.append(max(max_data_w, header_w))

    # Pre-build separator strings
    sep_str = (" " * padding) + divider + (" " * padding)

    # Determine max rows needed for data loop
    max_data_rows = max(len(col) for col in display_grid) if display_grid else 0

    user_input = ""
    while not validate_input(user_input):
        print(question)
        print()  # Spacer between question and table

        # --- A. Print Headers (if enabled) ---
        if use_headers:
            header_parts = []
            divider_parts = []

            for c, h_text in enumerate(headers):
                width = col_widths[c]

                # Format the header text
                cell = h_text.ljust(width)

                # Format the underline (using dashes matching column width)
                # You can change "-" to "=" if you prefer a double line
                div_line = ("-" * width)

                if c < len(headers) - 1:
                    header_parts.append(cell + sep_str)
                    divider_parts.append(div_line + sep_str)
                else:
                    header_parts.append(cell)
                    divider_parts.append(div_line)

            print("".join(header_parts))
            print("".join(divider_parts))

        # --- B. Print Data Rows ---
        for r in range(max_data_rows):
            line_parts = []
            for c in range(len(display_grid)):
                col_strs = display_grid[c]
                width = col_widths[c]

                item_str = col_strs[r] if r < len(col_strs) else ""

                if c < len(display_grid) - 1:
                    cell = item_str.ljust(width)
                    line_parts.append(cell + sep_str)
                else:
                    line_parts.append(item_str)

            print("".join(line_parts))
        print()

        user_input = get_input()
        if not validate_input(user_input):
            invalid_input()

    if user_input.isnumeric():
        return int(user_input)
    return flat_valid_options_lower.index(user_input.lower())


def invalid_input() -> None:
    print(f"{_RED}Invalid input{_RESET}\n")


def get_input(*, message: str = "Enter your choice", tip: str = "", end: str = ": ") -> str:
    result = input(f"{_ITALIC}{message}{f" ({tip})" if len(tip) > 0 else ''}{end}{_RESET}")
    return result.strip()


def log(msg: str) -> None:
    print(f"{msg}{_RESET}")


def warn(msg: str) -> None:
    print(f"{_YELLOW}{msg}{_RESET}")


def error(msg: str) -> None:
    print(f"{_RED}{msg}{_RESET}")


def print_table(values: list[Sequence[Any]], headers: tuple[str, ...] | None = None) -> None:
    if len(values) == 0:
        _print_empty_table(headers)
        return

    if headers is not None and len(headers) != len(values[0]):
        raise ValueError("The number of columns does not match the number of headers")

    string_rows: list[list[str]] = []
    for row in values:
        string_row = []
        for value in row:
            string_row.append(str(value))
        string_rows.append(string_row)

    column_max_lengths = _get_column_widths(string_rows, headers)

    rows: list[Sequence[str]] = []

    if headers is not None:
        rows.append(headers)
        rows.append(tuple('-' * max_length for max_length in column_max_lengths))

    rows.extend(string_rows)

    for row in rows:
        log(_get_table_row(row, column_max_lengths))


def _get_column_widths(rows: list[Sequence[str]], headers: Sequence[str] | None) -> list[int]:
    column_max_lengths = [0] * len(rows[0])

    if headers is not None:
        for i in range(len(headers)):
            column_max_lengths[i] = max(column_max_lengths[i], len(headers[i]))

    for i in range(len(rows)):
        for j in range(len(rows[i])):
            column_max_lengths[j] = max(column_max_lengths[j], len(rows[i][j]))

    return column_max_lengths


def _print_empty_table(headers: tuple[str, ...] | None) -> None:
    """Helper to handle the empty table logic."""
    if headers is None:
        warn("Empty table")
    else:
        log("  |  ".join(headers))
        log("  |  ".join('-' * len(h) for h in headers))


def _get_table_row(row: Sequence[str], column_max_lengths: Sequence[int]) -> str:
    line = [row[0], ' ' * (column_max_lengths[0] - len(row[0]))]
    for i in range(1, len(row)):
        line.append('  |  ')
        line.append(row[i])
        line.append(' ' * (column_max_lengths[i] - len(row[i])))
    return ''.join(line)


if __name__ == '__main__':
    # log("Testing...")
    # print()
    # print(ask_for_bool("Do you want me to do it?"))
    print("'io_ulits.py' testing\n")
    options = [
        "Change database path",
        "Change database filename",
        "Override the file (file will be permanently lost)",
        None,
        "Cancel database setup"
    ]
    selection = ask_for_choice(options)
    print(f"\nYou've selected: '{selection}'")
