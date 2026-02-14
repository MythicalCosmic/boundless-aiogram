#!/usr/bin/env python3
import sys

from boundless_aiogram.core import Colors, print_colored, print_banner, print_error


HELP_TEXT = f"""
{Colors.BOLD}Usage:{Colors.ENDC}
  boundless <command> [options]

{Colors.BOLD}Commands:{Colors.ENDC}
  {Colors.GREEN}new{Colors.ENDC}                Create a new bot project (interactive wizard)
  {Colors.GREEN}run{Colors.ENDC}                Start the bot
  {Colors.GREEN}makemigrations{Colors.ENDC}     Generate new database migration
  {Colors.GREEN}migrate{Colors.ENDC}            Apply pending migrations
  {Colors.GREEN}rollback{Colors.ENDC}           Rollback last migration
  {Colors.GREEN}flush{Colors.ENDC}              Drop all tables and re-migrate
  {Colors.GREEN}help{Colors.ENDC}               Show this help message

{Colors.BOLD}Examples:{Colors.ENDC}
  {Colors.DIM}boundless new{Colors.ENDC}
  {Colors.DIM}boundless run{Colors.ENDC}
  {Colors.DIM}boundless makemigrations "added order status"{Colors.ENDC}
  {Colors.DIM}boundless migrate{Colors.ENDC}
  {Colors.DIM}boundless rollback{Colors.ENDC}
  {Colors.DIM}boundless flush{Colors.ENDC}
"""


def show_help():
    print_banner()
    print(HELP_TEXT)


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "new":
        from boundless_aiogram.commands.new import cmd_new
        cmd_new()

    elif command == "run":
        from boundless_aiogram.commands.run import cmd_run
        cmd_run()

    elif command == "makemigrations":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        from boundless_aiogram.commands.migrate import cmd_makemigrations
        cmd_makemigrations(message)

    elif command == "migrate":
        from boundless_aiogram.commands.migrate import cmd_migrate
        cmd_migrate()

    elif command == "rollback":
        from boundless_aiogram.commands.migrate import cmd_rollback
        cmd_rollback()

    elif command == "flush":
        from boundless_aiogram.commands.migrate import cmd_flush
        cmd_flush()

    elif command in ("help", "-h", "--help"):
        show_help()

    else:
        print_error(f"Unknown command: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()