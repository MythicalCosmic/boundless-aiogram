#!/usr/bin/env python3
import sys

from boundless_aiogram import Colors, print_banner
from boundless_aiogram.core import print_colored, print_error


VERSION = "2.0.0"

HELP_TEXT = f"""
  {Colors.BOLD}{Colors.WHITE}Usage:{Colors.ENDC}
    boundless <command> [options]

  {Colors.BOLD}{Colors.WHITE}Project Commands:{Colors.ENDC}
    {Colors.GREEN}new{Colors.ENDC}                Create a new bot project (interactive wizard)
    {Colors.GREEN}run{Colors.ENDC}                Start the bot (polling or webhook)
    {Colors.GREEN}info{Colors.ENDC}               Show current project info
    {Colors.GREEN}django{Colors.ENDC}             Switch project to Django ORM integration

    
  {Colors.BOLD}{Colors.WHITE}Database Commands:{Colors.ENDC}
    {Colors.GREEN}makemigrations{Colors.ENDC}     Generate a new database migration
    {Colors.GREEN}migrate{Colors.ENDC}            Apply pending migrations
    {Colors.GREEN}rollback{Colors.ENDC}           Rollback the last migration
    {Colors.GREEN}flush{Colors.ENDC}              Drop all tables and re-migrate

  {Colors.BOLD}{Colors.WHITE}Other:{Colors.ENDC}
    {Colors.GREEN}version{Colors.ENDC}            Show version
    {Colors.GREEN}help{Colors.ENDC}               Show this help message

  {Colors.BOLD}{Colors.WHITE}Examples:{Colors.ENDC}
    {Colors.DIM}boundless new{Colors.ENDC}
    {Colors.DIM}boundless run{Colors.ENDC}
    {Colors.DIM}boundless run --webhook{Colors.ENDC}
    {Colors.DIM}boundless makemigrations "added user table"{Colors.ENDC}
    {Colors.DIM}boundless migrate{Colors.ENDC}
    {Colors.DIM}boundless django{Colors.ENDC}
"""


def show_help():
    print_banner()
    print(HELP_TEXT)


def show_version():
    print_colored(f"  boundless v{VERSION}", Colors.CYAN + Colors.BOLD)


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "new":
        from boundless_aiogram.commands.new import cmd_new
        cmd_new()

    elif command == "run":
        from boundless_aiogram.commands.run import cmd_run
        cmd_run()

    elif command == "info":
        from boundless_aiogram.commands.info import cmd_info
        cmd_info()

    elif command == "django":
        from boundless_aiogram.commands.django_switch import cmd_django
        cmd_django()

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

    elif command in ("version", "-v", "--version"):
        show_version()

    elif command in ("help", "-h", "--help"):
        show_help()

    else:
        print_error(f"Unknown command: {command}")
        print_colored(f"\n  Run {Colors.CYAN}boundless help{Colors.ENDC} to see available commands.\n", Colors.DIM)
        sys.exit(1)


if __name__ == "__main__":
    main()
