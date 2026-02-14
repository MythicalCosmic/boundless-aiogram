import sys
from typing import Optional

from boundless_aiogram.core import print_error, print_success, print_warning, print_info
from boundless_aiogram.core.prompt import ask_confirm
from boundless_aiogram.core.shell import run_command, find_project_root
from boundless_aiogram.core.config import load_config


def _get_project_root() -> str:
    root = find_project_root()
    if not root:
        print_error("Not inside a Boundless project")
        sys.exit(1)

    config = load_config(root)
    if config and not config.get("use_migrations"):
        print_error("Migrations are not enabled for this project")
        print_info("Recreate the project with migrations enabled")
        sys.exit(1)

    return root


def cmd_makemigrations(message: Optional[str] = None):
    root = _get_project_root()
    message = message or "auto"

    print_info(f'Generating migration: "{message}"')
    success = run_command(
        ["alembic", "revision", "--autogenerate", "-m", message],
        cwd=root,
    )

    if success:
        print_success("Migration created")
    else:
        print_error("Failed to create migration")
        sys.exit(1)


def cmd_migrate():
    root = _get_project_root()

    print_info("Applying migrations...")
    success = run_command(["alembic", "upgrade", "head"], cwd=root)

    if success:
        print_success("Migrations applied")
    else:
        print_error("Migration failed")
        sys.exit(1)


def cmd_rollback():
    root = _get_project_root()

    print_info("Rolling back last migration...")
    success = run_command(["alembic", "downgrade", "-1"], cwd=root)

    if success:
        print_success("Rollback complete")
    else:
        print_error("Rollback failed")
        sys.exit(1)


def cmd_flush():
    root = _get_project_root()

    try:
        confirmed = ask_confirm(
            "This will DROP all tables and re-migrate. Are you sure?",
            default=False,
        )
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)

    if not confirmed:
        print_info("Cancelled")
        return

    print_warning("Flushing database...")

    run_command(["alembic", "downgrade", "base"], cwd=root)
    success = run_command(["alembic", "upgrade", "head"], cwd=root)

    if success:
        print_success("Database flushed and re-migrated")
    else:
        print_error("Flush failed")
        sys.exit(1)