import sys
import time
from pathlib import Path

from boundless_aiogram.core import Colors, print_colored
from boundless_aiogram.core.constants import DEPENDENCIES, DIRECTORIES
from boundless_aiogram.core.loader import Loader
from boundless_aiogram.core.shell import run_command, pip_freeze
from boundless_aiogram.templates import TEMPLATES, ALEMBIC_ENV_TEMPLATE


def create_directory_structure(project_path: Path):
    for directory in DIRECTORIES:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)

        if not directory.startswith("logs"):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")


def create_project_files(project_path: Path, project_name: str):
    for file_path, content in TEMPLATES.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        content = content.replace("{project_name}", project_name)
        full_path.write_text(content)


def setup_alembic(project_path: Path):
    if not run_command(["alembic", "init", "migrations"], cwd=str(project_path)):
        print_colored("\n[!] Warning: Alembic initialization failed", Colors.YELLOW)
        return

    alembic_ini = project_path / "alembic.ini"
    if alembic_ini.exists():
        content = alembic_ini.read_text()
        content = content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname",
            "# sqlalchemy.url = # Set in migrations/env.py",
        )
        alembic_ini.write_text(content)

    env_path = project_path / "migrations" / "env.py"
    if env_path.exists():
        env_path.write_text(ALEMBIC_ENV_TEMPLATE)

    run_command(
        ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
        cwd=str(project_path),
    )
    run_command(["alembic", "upgrade", "head"], cwd=str(project_path))


def create_new_project(project_name: str):
    project_path = Path(project_name)

    if project_path.exists():
        print_colored(f"\n[✗] Project '{project_name}' already exists\n", Colors.RED)
        sys.exit(1)

    print_colored(
        f"\nInitializing project: {Colors.BOLD}{project_name}{Colors.ENDC}\n",
        Colors.BLUE,
    )

    with Loader("Creating project structure"):
        project_path.mkdir()
        create_directory_structure(project_path)
        time.sleep(0.2)

    with Loader("Generating project files"):
        create_project_files(project_path, project_name)
        time.sleep(0.3)

    with Loader("Installing dependencies"):
        if not run_command(
            [sys.executable, "-m", "pip", "install", "-q"] + DEPENDENCIES,
            cwd=str(project_path),
        ):
            print_colored(
                "\n[!] Warning: Failed to install some dependencies", Colors.YELLOW
            )

    with Loader("Generating requirements.txt"):
        output = pip_freeze(str(project_path))
        (project_path / "requirements.txt").write_text(output)

    with Loader("Setting up Alembic"):
        setup_alembic(project_path)

    print_colored(
        f"\n{Colors.GREEN}{Colors.BOLD}Project created successfully!{Colors.ENDC}\n",
        Colors.GREEN,
    )
    print_colored("Next steps:", Colors.CYAN + Colors.BOLD)
    print_colored(f"  1. cd {project_name}", Colors.DIM)
    print_colored(f"  2. cp .env.example .env", Colors.DIM)
    print_colored(f"  3. Edit .env and add your BOT_TOKEN", Colors.DIM)
    print_colored(f"  4. python main.py\n", Colors.DIM)