from boundless_aiogram import Colors, print_colored, print_banner


def print_error(message: str):
    print_colored(f"  [x] {message}", Colors.RED)


def print_success(message: str):
    print_colored(f"  [*] {message}", Colors.GREEN)


def print_warning(message: str):
    print_colored(f"  [!] {message}", Colors.YELLOW)


def print_info(message: str):
    print_colored(f"  [~] {message}", Colors.CYAN)
