from typing import Optional
from boundless_aiogram import Colors


def ask_text(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    print(f"\n  {Colors.CYAN}{Colors.BOLD}? {question}{suffix}{Colors.ENDC}")
    value = input(f"    {Colors.GREEN}>{Colors.ENDC} ").strip()
    return value or default


def ask_select(question: str, options: dict, default: int = 0) -> str:
    keys = list(options.keys())
    print(f"\n  {Colors.CYAN}{Colors.BOLD}? {question}{Colors.ENDC}")
    for i, label in enumerate(options.values()):
        if i == default:
            marker = f"{Colors.GREEN}>{Colors.ENDC}"
            line = f"{Colors.BOLD}{label}{Colors.ENDC}"
        else:
            marker = " "
            line = f"{Colors.DIM}{label}{Colors.ENDC}"
        print(f"    {marker} {i + 1}) {line}")

    while True:
        value = input(f"    {Colors.GREEN}>{Colors.ENDC} ").strip()
        if not value:
            return keys[default]
        try:
            idx = int(value) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            pass
        print(f"    {Colors.RED}Enter a number between 1 and {len(keys)}{Colors.ENDC}")


def ask_multi_select(question: str, options: dict, defaults: Optional[list] = None) -> list:
    keys = list(options.keys())
    defaults = defaults or []
    default_indices = [keys.index(d) for d in defaults if d in keys]

    print(f"\n  {Colors.CYAN}{Colors.BOLD}? {question} {Colors.DIM}(comma-separated, e.g. 1,3){Colors.ENDC}")
    for i, label in enumerate(options.values()):
        if i in default_indices:
            marker = f"{Colors.GREEN}[x]{Colors.ENDC}"
        else:
            marker = f"{Colors.DIM}[ ]{Colors.ENDC}"
        print(f"    {marker} {i + 1}) {label}")

    while True:
        value = input(f"    {Colors.GREEN}>{Colors.ENDC} ").strip()
        if not value:
            return defaults

        try:
            indices = [int(x.strip()) - 1 for x in value.split(",")]
            if all(0 <= idx < len(keys) for idx in indices):
                return [keys[idx] for idx in indices]
        except ValueError:
            pass
        print(f"    {Colors.RED}Enter numbers 1-{len(keys)} separated by commas{Colors.ENDC}")


def ask_confirm(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    print(f"\n  {Colors.CYAN}{Colors.BOLD}? {question} {suffix}{Colors.ENDC}")
    value = input(f"    {Colors.GREEN}>{Colors.ENDC} ").strip().lower()

    if not value:
        return default
    return value in ("y", "yes")
