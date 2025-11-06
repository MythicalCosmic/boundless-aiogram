#!/usr/bin/env python3
"""
Boundless-Aiogram CLI
A modern framework for building Telegram bots with aiogram
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List

# ASCII Banner
BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║ ██████╗  ██████╗ ██╗   ██╗███╗   ██╗██████╗ ██╗     ███████╗███████╗███████╗ ║
║ ██╔══██╗██╔═══██╗██║   ██║████╗  ██║██╔══██╗██║     ██╔════╝██╔════╝██╔════╝ ║
║ ██████╔╝██║   ██║██║   ██║██╔██╗ ██║██║  ██║██║     █████╗  ███████╗███████╗ ║
║ ██╔══██╗██║   ██║██║   ██║██║╚██╗██║██║  ██║██║     ██╔══╝  ╚════██║╚════██║ ║
║ ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝███████╗███████╗███████║███████║ ║
║ ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝ ║
║                                                                              ║
║                      Modern Telegram Bot Framework                           ║
║                           Powered by Aiogram 3.x                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# Required dependencies
DEPENDENCIES = [
    "aiogram>=3.0.0",
    "alembic",
    "pyyaml",
    "sqlalchemy",
    "python-dotenv",
    "aiosqlite"
]

# File Templates
TEMPLATES = {
    'main.py': '''"""
Main bot entry point
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from core.config import config
from core.logging import setup_logging
from database.database import init_db
from bot.handlers import register_handlers

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

async def main():
    """Initialize and start the bot"""
    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    await init_db()
    logger.info("Database initialized")
    
    register_handlers(dp)
    logger.info("Handlers registered")
    
    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
''',
    
    'core/config.py': '''"""
Configuration management
"""
import os
from dataclasses import dataclass

@dataclass
class Config:
    """Bot configuration"""
    bot_token: str
    database_url: str
    admin_ids: list[int]
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            bot_token=os.getenv("BOT_TOKEN", ""),
            database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot_database.db"),
            admin_ids=[int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
        )

config = Config.from_env()
''',
    
    'core/logging.py': '''"""
Logging configuration
"""
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Configure logging for the application"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                f"{log_dir}/bot.log",
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
''',
    
    'database/database.py': '''"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.models.base import Base
from core.config import config

engine = create_async_engine(config.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session
''',
    
    'database/models/base.py': '''"""
Base model class
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all models"""
    pass
''',
    
    'database/models/user.py': '''"""
User model
"""
from sqlalchemy import Column, BigInteger, String, DateTime
from datetime import datetime
from database.models.base import Base

class User(Base):
    """User model for storing Telegram user data"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    state = Column(String, default="idle")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
''',
    
    'bot/handlers/__init__.py': '''"""
Handler registration
"""
from aiogram import Dispatcher
from bot.handlers import commands, messages, callbacks

def register_handlers(dp: Dispatcher):
    """Register all handlers"""
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    dp.include_router(callbacks.router)
''',
    
    'bot/handlers/commands.py': '''"""
Command handlers
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.keyboards.inline import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    await message.answer(
        f"Hello, {message.from_user.first_name}!\\n\\n"
        "Welcome to your bot powered by Boundless-Aiogram.",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    await message.answer(
        "Available commands:\\n"
        "/start - Start the bot\\n"
        "/help - Show this help message"
    )
''',
    
    'bot/handlers/messages.py': '''"""
Message handlers
"""
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def echo_message(message: Message):
    """Echo all text messages"""
    await message.answer(f"You said: {message.text}")
''',
    
    'bot/handlers/callbacks.py': '''"""
Callback query handlers
"""
from aiogram import Router
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query()
async def handle_callback(callback: CallbackQuery):
    """Handle callback queries"""
    await callback.answer("Button clicked!")
''',
    
    'bot/keyboards/inline.py': '''"""
Inline keyboards
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get main inline keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Button 1", callback_data="btn_1")],
        [InlineKeyboardButton(text="Button 2", callback_data="btn_2")]
    ])
    return keyboard
''',
    
    'bot/keyboards/reply.py': '''"""
Reply keyboards
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Get main reply keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Option 1")],
            [KeyboardButton(text="Option 2")]
        ],
        resize_keyboard=True
    )
    return keyboard
''',
    
    'bot/middlewares/auth.py': '''"""
Authentication middleware
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Add authentication logic here
        return await handler(event, data)
''',
    
    'bot/middlewares/throttling.py': '''"""
Throttling middleware
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, rate_limit: int = 1):
        self.rate_limit = rate_limit
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Add rate limiting logic here
        return await handler(event, data)
''',
    
    'bot/filters/custom.py': '''"""
Custom filters
"""
from aiogram.filters import Filter
from aiogram.types import Message

class IsAdminFilter(Filter):
    """Filter for admin users"""
    
    async def __call__(self, message: Message) -> bool:
        from core.config import config
        return message.from_user.id in config.admin_ids
''',
    
    'bot/states/user.py': '''"""
FSM states
"""
from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    """User FSM states"""
    idle = State()
    waiting_for_input = State()
    processing = State()
''',
    
    'utils/helpers.py': '''"""
Helper functions
"""

def format_user_mention(user_id: int, name: str) -> str:
    """Format user mention for HTML"""
    return f'<a href="tg://user?id={user_id}">{name}</a>'
''',
    
    '.env.example': '''# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./bot_database.db

# Optional: PostgreSQL example
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Admin User IDs (comma-separated)
ADMIN_IDS=123456789,987654321
''',
    
    '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Alembic
migrations/versions/__pycache__/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
''',
    
    'README.md': '''# {project_name}

A modern Telegram bot built with **Boundless-Aiogram** framework.

## Features

- Modern async/await syntax with Aiogram 3.x
- SQLAlchemy async ORM for database operations
- FSM (Finite State Machine) support
- Middleware system for authentication and rate limiting
- Custom filters and keyboards
- Structured project layout for scalability
- Alembic database migrations
- Comprehensive logging system

## Project Structure

```
{project_name}/
├── bot/
│   ├── handlers/        # Message and callback handlers
│   ├── middlewares/     # Custom middlewares
│   ├── filters/         # Custom filters
│   ├── keyboards/       # Keyboard layouts
│   └── states/          # FSM states
├── database/
│   ├── models/          # Database models
│   └── database.py      # Database configuration
├── core/
│   ├── config.py        # Configuration management
│   └── logging.py       # Logging setup
├── utils/               # Helper functions
├── migrations/          # Alembic migrations
├── tests/               # Unit tests
└── main.py              # Bot entry point
```

## Setup

1. **Clone and navigate to the project:**
   ```bash
   cd {project_name}
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your bot token and other settings.

5. **Initialize database:**
   ```bash
   alembic upgrade head
   ```

6. **Run the bot:**
   ```bash
   python main.py
   ```

## Development

### Adding New Handlers

Create handler files in `bot/handlers/` and register them in `bot/handlers/__init__.py`.

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Adding Middleware

Create middleware in `bot/middlewares/` and register it in your dispatcher.

## Contributing

Built with [Boundless-Aiogram](https://github.com/yourusername/boundless-aiogram)

## License

MIT License
''',

    'tests/__init__.py': '''"""
Test suite for the bot
"""
''',
}

def print_colored(message: str, color: str = Colors.ENDC):
    """Print colored message"""
    print(f"{color}{message}{Colors.ENDC}")

def print_banner():
    """Display the Boundless banner"""
    print_colored(BANNER, Colors.CYAN + Colors.BOLD)

class Loader:
    """Simple loading animation"""
    def __init__(self, message: str):
        self.message = message
        self.running = False
        
    def __enter__(self):
        self.running = True
        print(f"{Colors.YELLOW}[•] {self.message}", end="", flush=True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if exc_type is None:
            print(f"\r{Colors.GREEN}[✓] {self.message}{Colors.ENDC}")
        else:
            print(f"\r{Colors.RED}[✗] {self.message}{Colors.ENDC}")
        return False

def run_command(command: List[str], cwd: str = None) -> bool:
    """Execute a shell command"""
    try:
        result = subprocess.run(
            command,
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print_colored(f"\n    {e.stderr.strip()}", Colors.RED + Colors.DIM)
        return False

def create_directory_structure(project_path: Path):
    """Create the project directory structure"""
    directories = [
        "bot/handlers",
        "bot/middlewares",
        "bot/filters",
        "bot/keyboards",
        "bot/states",
        "database/models",
        "core",
        "utils",
        "tests",
        "logs",
    ]
    
    for directory in directories:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        if not directory.startswith("logs"):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                module_name = directory.replace('/', '.')
                init_file.write_text(f'"""\n{module_name}\n"""\n')

def create_project_files(project_path: Path, project_name: str):
    """Create all project files from templates"""
    for file_path, content in TEMPLATES.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Replace placeholders
        content = content.replace('{project_name}', project_name)
        full_path.write_text(content)

def create_new_project(project_name: str):
    """Create a new Boundless-Aiogram project"""
    print_banner()
    
    project_path = Path(project_name)
    
    if project_path.exists():
        print_colored(f"\n[✗] Project '{project_name}' already exists\n", Colors.RED)
        sys.exit(1)
    
    print_colored(f"\nInitializing project: {Colors.BOLD}{project_name}{Colors.ENDC}\n", Colors.BLUE)
    
    with Loader("Creating project structure"):
        project_path.mkdir()
        create_directory_structure(project_path)
        time.sleep(0.2)
    
    with Loader("Generating project files"):
        create_project_files(project_path, project_name)
        time.sleep(0.3)
    
    with Loader("Installing dependencies"):
        if not run_command([sys.executable, "-m", "pip", "install", "-q"] + DEPENDENCIES, cwd=str(project_path)):
            print_colored("\n[!] Warning: Failed to install some dependencies", Colors.YELLOW)
    
    with Loader("Generating requirements.txt"):
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            cwd=str(project_path),
            capture_output=True,
            text=True
        )
        (project_path / "requirements.txt").write_text(result.stdout)
    
    with Loader("Initializing Alembic"):
        if not run_command(["alembic", "init", "migrations"], cwd=str(project_path)):
            print_colored("\n[!] Warning: Alembic initialization failed", Colors.YELLOW)
    
    # Update Alembic configuration
    alembic_ini = project_path / "alembic.ini"
    if alembic_ini.exists():
        with Loader("Configuring Alembic"):
            content = alembic_ini.read_text()
            content = content.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                "# sqlalchemy.url = # Set in migrations/env.py"
            )
            alembic_ini.write_text(content)
    
    # Update Alembic env.py
    env_path = project_path / "migrations" / "env.py"
    if env_path.exists():
        with Loader("Setting up database migrations"):
            env_content = '''"""
Alembic environment configuration
"""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.models.base import Base
from core.config import config as app_config

# Alembic Config object
config = context.config

# Set SQLAlchemy URL from app config
config.set_main_option("sqlalchemy.url", app_config.database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode"""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
            env_path.write_text(env_content)
    
    with Loader("Creating initial migration"):
        run_command(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], cwd=str(project_path))
    
    with Loader("Applying migrations"):
        run_command(["alembic", "upgrade", "head"], cwd=str(project_path))
    
    print_colored(f"\n{Colors.GREEN}{Colors.BOLD}Project created successfully!{Colors.ENDC}\n", Colors.GREEN)
    print_colored(f"Next steps:", Colors.CYAN + Colors.BOLD)
    print_colored(f"  1. cd {project_name}", Colors.DIM)
    print_colored(f"  2. cp .env.example .env", Colors.DIM)
    print_colored(f"  3. Edit .env and add your BOT_TOKEN", Colors.DIM)
    print_colored(f"  4. python main.py\n", Colors.DIM)

def show_help():
    """Display help information"""
    print_banner()
    print_colored("\nUsage:", Colors.BOLD)
    print_colored("  boundless new <project_name>    Create a new bot project", Colors.DIM)
    print_colored("  boundless help                   Show this help message\n", Colors.DIM)

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "new":
        if len(sys.argv) < 3:
            print_colored("\n[✗] Error: Project name required\n", Colors.RED)
            print_colored("Usage: boundless new <project_name>\n", Colors.DIM)
            sys.exit(1)
        create_new_project(sys.argv[2])
    elif command == "help" or command == "-h" or command == "--help":
        show_help()
    else:
        print_colored(f"\n[✗] Unknown command: {command}\n", Colors.RED)
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()