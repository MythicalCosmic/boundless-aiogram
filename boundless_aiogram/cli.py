#!/usr/bin/env python3
import sys

from boundless_aiogram.core import Colors, print_colored, print_banner
from boundless_aiogram.commands.new import create_new_project


def show_help():
    print_banner()
    print_colored("\nUsage:", Colors.BOLD)
    print_colored("  boundless new <project_name>    Create a new bot project", Colors.DIM)
    print_colored("  boundless help                   Show this help message\n", Colors.DIM)


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "new":
        if len(sys.argv) < 3:
            print_colored("\n[✗] Error: Project name required\n", Colors.RED)
            print_colored("Usage: boundless new <project_name>\n", Colors.DIM)
            sys.exit(1)
        print_banner()
        create_new_project(sys.argv[2])

    elif command in ("help", "-h", "--help"):
        show_help()

    else:
        print_colored(f"\n[✗] Unknown command: {command}\n", Colors.RED)
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()