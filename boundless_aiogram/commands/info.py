import sys

from boundless_aiogram import Colors
from boundless_aiogram.core import print_error, print_colored
from boundless_aiogram.core.config import load_config
from boundless_aiogram.core.shell import find_project_root


def cmd_info():
    root = find_project_root()
    if not root:
        print_error("Not inside a Boundless project.")
        sys.exit(1)

    config = load_config(root)
    if not config:
        print_error("Could not read .boundless.yml")
        sys.exit(1)

    print()
    print_colored("  ╔═══════════════════════════════════════════╗", Colors.CYAN)
    print_colored("  ║           Project Information              ║", Colors.CYAN)
    print_colored("  ╚═══════════════════════════════════════════╝", Colors.CYAN)
    print()
    print_colored(f"  Project:   {Colors.BOLD}{config.get('project_name', 'unknown')}{Colors.ENDC}", Colors.WHITE)
    print_colored(f"  Template:  {config.get('template', 'default')}", Colors.DIM)
    print_colored(f"  Database:  {config.get('database', 'sqlalchemy')}", Colors.DIM)
    print_colored(f"  Server:    {config.get('server_mode', 'polling')}", Colors.DIM)
    extras = config.get("extras", [])
    if extras:
        print_colored(f"  Extras:    {', '.join(extras)}", Colors.DIM)
    print()
