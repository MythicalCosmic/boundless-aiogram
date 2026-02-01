# boundless-aiogram

> Production-ready Telegram bot framework with CLI scaffolding — powering bots with 1000s of users

[![PyPI version](https://badge.fury.io/py/boundless-aiogram.svg)](https://pypi.org/project/boundless-aiogram/)
[![Downloads](https://static.pepy.tech/badge/boundless-aiogram)](https://pepy.tech/project/boundless-aiogram)
[![Python](https://img.shields.io/pypi/pyversions/boundless-aiogram)](https://pypi.org/project/boundless-aiogram/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**boundless-aiogram** is a battle-tested bot framework built on top of aiogram 3.x. It provides a complete project structure, CLI tools, and best practices out of the box — so you can focus on building features, not boilerplate.

**2,000+ downloads** and counting. Used in production bots serving **thousands of users**.

---

## 🚀 Bots Built With This Framework

| Bot | Users | Monthly Activity |
|-----|-------|------------------|
| Smart English HR | 1,200+ | 100+ applications |
| Cake Bot | 200+ | Active daily |
| + More in production | — | — |

---

## ✨ Features

- 🛠️ **CLI Scaffolding** — Generate new bot projects instantly
- 📁 **Production Structure** — Organized handlers, database, utils, languages
- 🗄️ **Database Layer** — SQLAlchemy + Alembic migrations built-in
- 🌍 **Multi-language** — i18n support out of the box
- ⚙️ **Core Module** — Config and middleware ready to go
- 🧪 **Test Setup** — Testing structure included
- 📤 **File Uploads** — Upload handling utilities

---

## 📦 Installation

```bash
pip install boundless-aiogram
```

---

## 🚀 Quick Start

### Create a New Bot Project

```bash
# Generate new project
boundless-aiogram init my-awesome-bot

# Navigate to project
cd my-awesome-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your bot token

# Run migrations
alembic upgrade head

# Start your bot
python main.py
```

That's it. You're ready to build.

---

## 📁 Generated Project Structure

```
my-awesome-bot/
│
├── bot/                    # Bot handlers and logic
│   ├── handlers/          # Message & callback handlers
│   ├── keyboards/         # Inline & reply keyboards
│   ├── states/            # FSM states
│   └── filters/           # Custom filters
│
├── core/                   # Core configuration
│   ├── config.py          # Settings management
│   └── middleware.py      # Bot middleware
│
├── database/               # Database layer
│   ├── models.py          # SQLAlchemy models
│   ├── crud.py            # CRUD operations
│   └── session.py         # DB session management
│
├── languages/              # Internationalization
│   ├── en.py              # English
│   ├── uz.py              # Uzbek
│   └── ru.py              # Russian
│
├── migrations/             # Alembic migrations
│   └── versions/          # Migration files
│
├── utils/                  # Utility functions
│   └── helpers.py         # Common helpers
│
├── tests/                  # Test suite
│
├── main.py                 # Entry point
├── alembic.ini            # Alembic config
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── .gitignore             # Git ignore
```

---

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `boundless-aiogram init <name>` | Create new bot project |
| `boundless-aiogram --version` | Show version |
| `boundless-aiogram --help` | Show help |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          BOUNDLESS-AIOGRAM STRUCTURE            │
├─────────────────────────────────────────────────┤
│                                                 │
│   ┌─────────────────────────────────────────┐   │
│   │                BOT                      │   │
│   │   Handlers • Keyboards • States         │   │
│   └────────────────────┬────────────────────┘   │
│                        │                        │
│   ┌────────────────────▼────────────────────┐   │
│   │               CORE                      │   │
│   │       Config • Middleware               │   │
│   └────────────────────┬────────────────────┘   │
│                        │                        │
│   ┌────────┬───────────┴───────────┬────────┐   │
│   │        │                       │        │   │
│   ▼        ▼                       ▼        ▼   │
│ ┌──────┐ ┌────────┐ ┌───────────┐ ┌──────┐    │
│ │Utils │ │Database│ │ Languages │ │Tests │    │
│ │      │ │Alembic │ │   i18n    │ │      │    │
│ └──────┘ └────────┘ └───────────┘ └──────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📖 Usage Examples

### Basic Handler

```python
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Welcome! 🚀")
```

### Using Database

```python
from database.crud import create_user, get_user
from database.session import get_session

async def register_user(telegram_id: int, name: str):
    async with get_session() as session:
        user = await create_user(session, telegram_id, name)
        return user
```

### Multi-language Support

```python
from languages import get_text

async def greet(message: Message, lang: str = "en"):
    text = get_text("welcome", lang)
    await message.answer(text)
```

### FSM States

```python
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Bot
BOT_TOKEN=your-bot-token-from-botfather

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mybot
# Or SQLite:
# DATABASE_URL=sqlite:///bot.db

# Settings
ADMIN_IDS=123456789,987654321
DEFAULT_LANGUAGE=en
DEBUG=False
```

---

## 🗄️ Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add users table"

# Apply all migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View current version
alembic current
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=bot --cov=database
```

---

## 🚀 Deployment

### systemd (Linux)

```ini
[Unit]
Description=My Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/my-bot
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 📊 Why boundless-aiogram?

| Feature | boundless-aiogram | Starting from scratch |
|---------|-------------------|----------------------|
| Project setup | `1 command` | 30+ minutes |
| Database layer | ✅ Included | Manual setup |
| Migrations | ✅ Alembic ready | Manual setup |
| Multi-language | ✅ Built-in | Manual setup |
| Best practices | ✅ Enforced | Hope for the best |
| Production tested | ✅ 1000s of users | Unknown |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/MythicalCosmic/boundless-aiogram/issues)
- **PyPI:** [pypi.org/project/boundless-aiogram](https://pypi.org/project/boundless-aiogram/)

---

**Stop writing boilerplate. Start building bots.**
