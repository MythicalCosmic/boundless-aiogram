from typing import Optional
from boundless_aiogram.core import Colors


def ask_text(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    print(f"\n{Colors.CYAN}{Colors.BOLD}? {question}{suffix}{Colors.ENDC}")
    value = input(f"  {Colors.GREEN}>{Colors.ENDC} ").strip()
    return value or default


def ask_select(question: str, options: list[str], default: int = 0) -> int:
    print(f"\n{Colors.CYAN}{Colors.BOLD}? {question}{Colors.ENDC}")
    for i, option in enumerate(options):
        marker = f"{Colors.GREEN}●{Colors.ENDC}" if i == default else f"{Colors.DIM}○{Colors.ENDC}"
        print(f"  {marker} {i + 1}) {option}")

    while True:
        value = input(f"  {Colors.GREEN}>{Colors.ENDC} ").strip()
        if not value:
            return default
        try:
            idx = int(value) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        print(f"  {Colors.RED}Enter 1-{len(options)}{Colors.ENDC}")


def ask_multi_select(question: str, options: list[str], defaults: Optional[list[int]] = None) -> list[int]:
    defaults = defaults or []
    print(f"\n{Colors.CYAN}{Colors.BOLD}? {question} {Colors.DIM}(comma-separated, e.g. 1,3){Colors.ENDC}")
    for i, option in enumerate(options):
        marker = f"{Colors.GREEN}■{Colors.ENDC}" if i in defaults else f"{Colors.DIM}□{Colors.ENDC}"
        print(f"  {marker} {i + 1}) {option}")

    while True:
        value = input(f"  {Colors.GREEN}>{Colors.ENDC} ").strip()
        if not value:
            return defaults

        try:
            indices = [int(x.strip()) - 1 for x in value.split(",")]
            if all(0 <= idx < len(options) for idx in indices):
                return indices
        except ValueError:
            pass
        print(f"  {Colors.RED}Enter numbers 1-{len(options)} separated by commas{Colors.ENDC}")


def ask_confirm(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    print(f"\n{Colors.CYAN}{Colors.BOLD}? {question} {suffix}{Colors.ENDC}")
    value = input(f"  {Colors.GREEN}>{Colors.ENDC} ").strip().lower()

    if not value:
        return default
    return value in ("y", "yes")