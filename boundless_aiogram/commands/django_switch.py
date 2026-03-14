import sys
from pathlib import Path

from boundless_aiogram import Colors
from boundless_aiogram.core import print_error, print_success, print_info, print_colored, print_warning
from boundless_aiogram.core.config import load_config
from boundless_aiogram.core.prompt import ask_confirm
from boundless_aiogram.core.shell import find_project_root, run_command


def cmd_django():
    root = find_project_root()
    if not root:
        print_error("Not inside a Boundless project.")
        sys.exit(1)

    config = load_config(root)
    if not config:
        print_error("Could not read .boundless.yml")
        sys.exit(1)

    if config.get("database") == "django":
        print_info("This project already uses Django ORM.")
        return

    print()
    print_warning("This will switch your project from SQLAlchemy to Django ORM.")
    print_colored("  What this does:", Colors.BOLD)
    print_colored("    - Installs Django", Colors.DIM)
    print_colored("    - Creates django_app/ directory with models and settings", Colors.DIM)
    print_colored("    - Creates manage.py for Django management commands", Colors.DIM)
    print_colored("    - Updates .boundless.yml", Colors.DIM)
    print()
    print_colored("  What this does NOT do:", Colors.BOLD)
    print_colored("    - Does not remove existing database/ directory", Colors.DIM)
    print_colored("    - Does not remove Alembic (you can do this manually)", Colors.DIM)
    print()

    try:
        confirmed = ask_confirm("Proceed with Django integration?", default=False)
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)

    if not confirmed:
        print_info("Cancelled.")
        return

    project_path = Path(root)
    project_name = config.get("project_name", project_path.name)

    # Create Django app structure
    django_app = project_path / "django_app"
    for d in ["", "models", "management", "management/commands"]:
        (django_app / d).mkdir(parents=True, exist_ok=True)
        (django_app / d / "__init__.py").touch()

    # Write Django settings
    (django_app / "settings.py").write_text(f'''import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_app",
]

DATABASES = {{
    "default": {{
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}
}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
''')

    # Write manage.py
    (project_path / "manage.py").write_text('''#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
''')

    # Write runbot management command
    (django_app / "management" / "commands" / "runbot.py").write_text('''from django.core.management.base import BaseCommand
import asyncio


class Command(BaseCommand):
    help = "Start the Telegram bot"

    def handle(self, *args, **options):
        from main import main
        self.stdout.write("Starting bot via Django management command...")
        asyncio.run(main())
''')

    # Install Django
    print_info("Installing Django...")
    run_command([sys.executable, "-m", "pip", "install", "-q", "django>=4.2"])

    # Update config
    import yaml
    config["database"] = "django"
    config["use_migrations"] = False
    config_path = project_path / ".boundless.yml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print()
    print_success("Django integration added!")
    print()
    print_colored("  Next steps:", Colors.BOLD)
    print_colored("    1. Move your models to django_app/models/", Colors.DIM)
    print_colored("    2. Run: python manage.py makemigrations", Colors.DIM)
    print_colored("    3. Run: python manage.py migrate", Colors.DIM)
    print_colored("    4. Optionally remove database/ and alembic files", Colors.DIM)
    print()
