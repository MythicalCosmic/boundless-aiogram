# Boundless-Aiogram 🚀


**Boundless-Aiogram** is a modern, production-ready framework/template for building scalable **Telegram bots** with **Aiogram 3.x**. It provides a clean, structured architecture with built-in support for **async/await**, **database 
migrations**, **FSM**, and more.

## ✨ Features

- ⚡ **Modern async/await** syntax with Aiogram 3.x
- 🗄 **SQLAlchemy async ORM** for database operations
- 🔄 **Alembic migrations** for database versioning
- 📂 **Modular architecture** with organized handlers, middlewares, and filters
- 🎯 **FSM (Finite State Machine)** support for conversation flows
- 🛡️ **Built-in middleware** for authentication and rate limiting
- ⚙️ **Configuration management** with environment variables
- 📝 **Comprehensive logging** system with file rotation
- 🧪 **Test-ready** structure with dedicated test directory
- 🎨 **Modern CLI** with beautiful output and progress indicators

---

## 🚀 Installation

Install Boundless-Aiogram via pip:

```bash
pip install boundless-aiogram
```

---

## 📦 Quick Start

Create a new bot project with a single command:

```bash
boundless new mybot
```

Navigate to your project and set up:

```bash
cd mybot
cp .env.example .env
# Edit .env and add your BOT_TOKEN
python main.py
```

That's it! Your bot is now running.

---

## 🏗️ Project Structure

Boundless-Aiogram generates a clean, organized project structure:

```
mybot/
├── bot/
│   ├── handlers/          # Message and callback handlers
│   │   ├── commands.py    # Command handlers (/start, /help)
│   │   ├── messages.py    # Text message handlers
│   │   └── callbacks.py   # Callback query handlers
│   ├── middlewares/       # Custom middlewares
│   │   ├── auth.py        # Authentication middleware
│   │   └── throttling.py  # Rate limiting middleware
│   ├── filters/           # Custom filters
│   │   └── custom.py      # Custom filter examples
│   ├── keyboards/         # Keyboard layouts
│   │   ├── inline.py      # Inline keyboards
│   │   └── reply.py       # Reply keyboards
│   └── states/            # FSM states
│       └── user.py        # User conversation states
├── database/
│   ├── models/            # Database models
│   │   ├── base.py        # Base model class
│   │   └── user.py        # User model
│   └── database.py        # Database configuration
├── core/
│   ├── config.py          # Configuration management
│   └── logging.py         # Logging setup
├── utils/                 # Helper functions
│   └── helpers.py         # Utility functions
├── migrations/            # Alembic database migrations
├── tests/                 # Unit tests
├── logs/                  # Log files
├── main.py                # Bot entry point
├── .env.example           # Example environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration

Configure your bot using environment variables in `.env`:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./bot_database.db

# Optional: PostgreSQL
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Admin User IDs (comma-separated)
ADMIN_IDS=123456789,987654321
```

---

## 📚 Usage Examples

### Adding a New Command Handler

Create or edit `bot/handlers/commands.py`:

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(f"Hello, {message.from_user.first_name}!")
```

### Creating Custom Middleware

Edit `bot/middlewares/auth.py`:

```python
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Your authentication logic here
        user_id = event.from_user.id
        # Check if user is authorized
        return await handler(event, data)
```

### Using FSM States

Define states in `bot/states/user.py`:

```python
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_email = State()
```

Use in handlers:

```python
from aiogram.fsm.context import FSMContext
from bot.states.user import RegistrationStates

@router.message(Command("register"))
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer("What's your name?")

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.waiting_for_age)
    await message.answer("How old are you?")
```

---

## 🗄️ Database Management

### Creating Migrations

After modifying your models:

```bash
alembic revision --autogenerate -m "Added new field"
```

### Applying Migrations

```bash
alembic upgrade head
```

### Rolling Back

```bash
alembic downgrade -1
```

---

## 🧪 Testing

Run tests using pytest:

```bash
pytest tests/
```

---

## 📖 CLI Commands

```bash
boundless new <project_name>    # Create a new bot project
boundless help                  # Show help information
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🔗 Links

- **GitHub**: [github.com/MythicalCosmic/boundless-aiogram](https://github.com/yourMythicalCosmic/boundless-aiogram)
- **PyPI**: [pypi.org/project/boundless-aiogram](https://pypi.org/project/boundless-aiogram)

---

## 💡 Support

If you find this project helpful, consider giving it a ⭐ on GitHub!

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/MythicalCosmic/boundless-aiogram/issues).

---

**Built with ❤️ for the Telegram bot development community**