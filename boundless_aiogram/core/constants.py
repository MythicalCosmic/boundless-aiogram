TEMPLATES = {
    "default": "Default (Echo Bot)",
    "hr": "HR Bot (Recruitment & Vacancies)",
    "shop": "Shop Bot (Catalog, Cart & Orders)",
}

SERVER_MODES = {
    "polling": "Polling (Simple, recommended for dev)",
    "webhook": "Webhook (FastAPI, production-ready)",
    "both": "Both (Polling for dev, Webhook for prod)",
}

EXTRAS = {
    "rate_limiting": "Rate Limiting (limitless-py)",
    "redis": "Redis Caching",
    "i18n": "i18n (Multi-language)",
    "admin": "Admin Panel",
}

BASE_DEPENDENCIES = [
    "aiogram>=3.0.0",
    "sqlalchemy>=2.0.0",
    "python-dotenv",
    "aiosqlite",
    "pyyaml",
]

MIGRATION_DEPENDENCIES = [
    "alembic",
]

WEBHOOK_DEPENDENCIES = [
    "fastapi",
    "uvicorn[standard]",
]

EXTRA_DEPENDENCIES = {
    "rate_limiting": ["limitless-py"],
    "redis": ["redis[hiredis]", "aioredis"],
    "i18n": ["fluent.runtime"],
    "admin": [],
}

DIRECTORIES = [
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

I18N_DIRECTORIES = [
    "locales/uz",
    "locales/ru",
    "locales/en",
]

ADMIN_DIRECTORIES = [
    "bot/handlers/admin",
]