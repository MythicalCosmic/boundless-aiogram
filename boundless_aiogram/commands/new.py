import sys
import time
from pathlib import Path

from boundless_aiogram import Colors, print_banner
from boundless_aiogram.core import print_colored, print_success, print_error, print_info
from boundless_aiogram.core.constants import (
    TEMPLATE_CHOICES,
    SERVER_MODES,
    DATABASE_BACKENDS,
    EXTRAS,
    BASE_DEPENDENCIES,
    SQLALCHEMY_DEPENDENCIES,
    MIGRATION_DEPENDENCIES,
    DJANGO_DEPENDENCIES,
    WEBHOOK_DEPENDENCIES,
    EXTRA_DEPENDENCIES,
    DIRECTORIES,
    DJANGO_DIRECTORIES,
    I18N_DIRECTORIES,
    ADMIN_DIRECTORIES,
)
from boundless_aiogram.core.loader import Loader
from boundless_aiogram.core.prompt import ask_text, ask_select, ask_multi_select, ask_confirm
from boundless_aiogram.core.shell import run_command, pip_freeze
from boundless_aiogram.templates import get_template_files, get_alembic_env_template


def cmd_new():
    print_banner()
    print_colored("  Let's set up your new bot project.\n", Colors.DIM)

    try:
        project_name = ask_text("Project name", "my_bot")
        template = ask_select("Choose a template", TEMPLATE_CHOICES)
        database = ask_select("Database backend", DATABASE_BACKENDS)
        server_mode = ask_select("Server mode", SERVER_MODES)
        extras = ask_multi_select("Optional features", EXTRAS)
        use_i18n = "i18n" in extras
        use_admin = "admin" in extras
    except (KeyboardInterrupt, EOFError):
        print("\n")
        print_info("Cancelled.")
        sys.exit(0)

    options = {
        "template": template,
        "database": database,
        "server_mode": server_mode,
        "extras": extras,
    }

    project_path = Path(project_name)

    if project_path.exists():
        print_error(f"Directory '{project_name}' already exists.")
        sys.exit(1)

    print()
    print_colored(
        f"  Creating project: {Colors.BOLD}{Colors.WHITE}{project_name}{Colors.ENDC}",
        Colors.CYAN,
    )
    print_colored(
        f"  Template: {Colors.BOLD}{TEMPLATE_CHOICES[template]}{Colors.ENDC}",
        Colors.DIM,
    )
    print_colored(
        f"  Database: {Colors.BOLD}{DATABASE_BACKENDS[database]}{Colors.ENDC}",
        Colors.DIM,
    )
    print()

    # Create directory structure
    with Loader("Creating directory structure"):
        project_path.mkdir()
        dirs = DJANGO_DIRECTORIES if database == "django" else DIRECTORIES
        for directory in dirs:
            dir_path = project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            if not directory.startswith("logs"):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
        if use_i18n:
            for directory in I18N_DIRECTORIES:
                (project_path / directory).mkdir(parents=True, exist_ok=True)
        if use_admin:
            for directory in ADMIN_DIRECTORIES:
                dir_path = project_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                (dir_path / "__init__.py").write_text("")

    # Generate project files
    with Loader("Generating project files"):
        files = get_template_files(project_name, template, options)
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    # Install dependencies
    deps = list(BASE_DEPENDENCIES)
    if database == "django":
        deps += DJANGO_DEPENDENCIES
    else:
        deps += SQLALCHEMY_DEPENDENCIES
        deps += MIGRATION_DEPENDENCIES
    if server_mode in ("webhook", "both"):
        deps += WEBHOOK_DEPENDENCIES
    for extra in extras:
        deps += EXTRA_DEPENDENCIES.get(extra, [])

    with Loader("Installing dependencies"):
        if not run_command(
            [sys.executable, "-m", "pip", "install", "-q"] + deps,
            cwd=str(project_path),
        ):
            print_colored(
                "\n    Warning: Some dependencies may have failed to install.",
                Colors.YELLOW,
            )

    # Generate requirements.txt
    with Loader("Generating requirements.txt"):
        output = pip_freeze(str(project_path))
        (project_path / "requirements.txt").write_text(output)

    # Set up Alembic (only for SQLAlchemy)
    if database != "django":
        with Loader("Setting up Alembic migrations"):
            _setup_alembic(project_path)

    # Done!
    print()
    _print_success_box(project_name, database)


def _setup_alembic(project_path: Path):
    if not run_command(["alembic", "init", "migrations"], cwd=str(project_path)):
        return

    alembic_ini = project_path / "alembic.ini"
    if alembic_ini.exists():
        content = alembic_ini.read_text()
        content = content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            "# sqlalchemy.url = # Configured in migrations/env.py",
        )
        alembic_ini.write_text(content)

    env_path = project_path / "migrations" / "env.py"
    if env_path.exists():
        env_path.write_text(get_alembic_env_template())

    run_command(
        ["alembic", "revision", "--autogenerate", "-m", "initial"],
        cwd=str(project_path),
    )
    run_command(["alembic", "upgrade", "head"], cwd=str(project_path))


def _print_success_box(project_name: str, database: str):
    print_colored("  ╔═══════════════════════════════════════════╗", Colors.GREEN)
    print_colored("  ║   Project created successfully!           ║", Colors.GREEN)
    print_colored("  ╚═══════════════════════════════════════════╝", Colors.GREEN)
    print()
    print_colored("  Next steps:", Colors.BOLD + Colors.WHITE)
    print_colored(f"    1. cd {project_name}", Colors.DIM)
    print_colored(f"    2. cp .env.example .env", Colors.DIM)
    print_colored(f"    3. Edit .env and set your BOT_TOKEN", Colors.DIM)
    if database == "django":
        print_colored(f"    4. python manage.py migrate", Colors.DIM)
        print_colored(f"    5. python main.py", Colors.DIM)
    else:
        print_colored(f"    4. python main.py", Colors.DIM)
    print()
