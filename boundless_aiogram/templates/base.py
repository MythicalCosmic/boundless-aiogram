from typing import Dict


def get_base_files(project_name: str, options: dict) -> Dict[str, str]:
    use_django = options.get("database") == "django"
    server_mode = options.get("server_mode", "polling")
    files = {}

    files["main.py"] = _main_py(use_django, server_mode)
    files[".env.example"] = _env_example(use_django)
    files[".gitignore"] = _gitignore()
    files["Dockerfile"] = _dockerfile()
    files["docker-compose.yml"] = _docker_compose(use_django)
    files[".dockerignore"] = _dockerignore()
    files[".boundless.yml"] = _boundless_yml(project_name, options)
    files["core/__init__.py"] = ""
    files["core/config.py"] = _core_config(use_django)
    files["bot/__init__.py"] = ""
    files["bot/handlers/__init__.py"] = _handlers_init()
    files["bot/handlers/start.py"] = _start_handler()
    files["bot/keyboards/__init__.py"] = ""
    files["bot/states/__init__.py"] = ""
    files["bot/filters/__init__.py"] = ""
    files["bot/middlewares/__init__.py"] = ""
    files["utils/__init__.py"] = ""
    files["tests/__init__.py"] = ""

    if use_django:
        files.update(_django_files(project_name))
    else:
        files["database/__init__.py"] = ""
        files["database/models/__init__.py"] = _models_init()
        files["database/models/base.py"] = _db_base()
        files["database/models/user.py"] = _user_model()

    if server_mode in ("webhook", "both"):
        files["webhook/__init__.py"] = ""
        files["webhook/app.py"] = _webhook_app()

    return files


def _main_py(use_django: bool, server_mode: str) -> str:
    if use_django:
        return '''import asyncio
import logging
import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from core.config import settings
from bot.handlers import register_all_handlers


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    register_all_handlers(dp)

    logging.info("Bot starting in polling mode...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
'''
    return '''import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from core.config import settings
from bot.handlers import register_all_handlers


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    register_all_handlers(dp)

    logging.info("Bot starting in polling mode...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
'''


def _env_example(use_django: bool) -> str:
    base = '''BOT_TOKEN=
ADMIN_ID=

DATABASE_URL=sqlite+aiosqlite:///database.db

DEBUG=True
'''
    if use_django:
        base = '''BOT_TOKEN=
ADMIN_ID=

DJANGO_SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///db.sqlite3

DEBUG=True
'''
    return base


def _gitignore() -> str:
    return '''__pycache__/
*.py[cod]
*.sqlite3
*.db
.venv/
venv/
.env
migrations/versions/
.DS_Store
Thumbs.db
logs/*.log
*.egg-info/
dist/
build/
'''


def _dockerfile() -> str:
    return '''FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
'''


def _docker_compose(use_django: bool) -> str:
    base = '''services:
  bot:
    build: .
    env_file: .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
'''
    if use_django:
        base += '''
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: botdb
      POSTGRES_USER: botuser
      POSTGRES_PASSWORD: botpass
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
'''
    return base


def _dockerignore() -> str:
    return '''.git
.gitignore
.env
__pycache__
*.pyc
.venv
venv
.idea
.vscode
logs/
*.md
'''


def _boundless_yml(project_name: str, options: dict) -> str:
    extras = options.get("extras", [])
    return f'''project_name: {project_name}
template: {options.get("template", "default")}
server_mode: {options.get("server_mode", "polling")}
database: {options.get("database", "sqlalchemy")}
use_migrations: {str(options.get("database") != "django").lower()}
extras: [{", ".join(extras)}]
'''


def _core_config(use_django: bool) -> str:
    if use_django:
        return '''from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(getenv("ADMIN_ID", "0"))
    DEBUG: bool = getenv("DEBUG", "True").lower() == "true"


settings = Settings()
'''
    return '''from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(getenv("ADMIN_ID", "0"))
    DATABASE_URL: str = getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")
    DEBUG: bool = getenv("DEBUG", "True").lower() == "true"


settings = Settings()
'''


def _handlers_init() -> str:
    return '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
'''


def _start_handler() -> str:
    return '''from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome, <b>{message.from_user.full_name}</b>!\\n\\n"
        "This bot was created with Boundless framework."
    )
'''


def _models_init() -> str:
    return '''from database.models.base import Base
from database.models.user import User
'''


def _db_base() -> str:
    return '''from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
'''


def _user_model() -> str:
    return '''from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
'''


def _django_files(project_name: str) -> dict:
    return {
        "django_app/__init__.py": "",
        "django_app/settings.py": f'''import os
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
''',
        "django_app/models/__init__.py": '''from django_app.models.user import BotUser
''',
        "django_app/models/user.py": '''from django.db import models


class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, primary_key=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bot_users"

    def __str__(self):
        return f"{self.full_name} ({self.telegram_id})"
''',
        "django_app/management/__init__.py": "",
        "django_app/management/commands/__init__.py": "",
        "django_app/management/commands/runbot.py": '''from django.core.management.base import BaseCommand
import asyncio


class Command(BaseCommand):
    help = "Start the Telegram bot"

    def handle(self, *args, **options):
        from main import main
        self.stdout.write("Starting bot via Django management command...")
        asyncio.run(main())
''',
        "manage.py": '''#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
''',
    }


def _webhook_app() -> str:
    return '''from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request
from core.config import settings
from bot.handlers import register_all_handlers

app = FastAPI()
bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

register_all_handlers(dp)


@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://yourdomain.com/webhook"
    await bot.set_webhook(webhook_url)


@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await dp.feed_raw_update(bot=bot, update=update)
    return {"ok": True}


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
'''
