TEMPLATE_CHOICES = {
    "default": "Default -- Minimal Echo Bot",
    "hr": "HR Bot -- Recruitment & Vacancies",
    "fastfood": "Fast Food Bot -- Menu & Orders",
    "shop": "Shop Bot -- Catalog, Cart & Checkout",
    "booking": "Booking Bot -- Appointments & Scheduling",
    "education": "Education Bot -- Courses & Quizzes",
    "realestate": "Real Estate Bot -- Listings & Inquiries",
    "support": "Customer Support Bot -- Tickets & FAQ",
    "delivery": "Delivery Bot -- Tracking & Shipments",
    "news": "News Bot -- Broadcasts & Subscriptions",
    "restaurant": "Restaurant Bot -- Reservations & Menu",
    "fitness": "Fitness Bot -- Workouts & Progress",
}

SERVER_MODES = {
    "polling": "Polling (recommended for development)",
    "webhook": "Webhook (FastAPI, production-ready)",
    "both": "Both (polling for dev, webhook for prod)",
}

EXTRAS = {
    "rate_limiting": "Rate Limiting (limitless-py)",
    "redis": "Redis Caching",
    "i18n": "i18n (Multi-language support)",
    "admin": "Admin Panel",
}

DATABASE_BACKENDS = {
    "sqlalchemy": "SQLAlchemy + Alembic (standalone)",
    "django": "Django ORM (for Django integration)",
}

BASE_DEPENDENCIES = [
    "aiogram>=3.0.0",
    "python-dotenv",
    "pyyaml",
]

SQLALCHEMY_DEPENDENCIES = [
    "sqlalchemy>=2.0.0",
    "aiosqlite",
]

MIGRATION_DEPENDENCIES = [
    "alembic",
]

DJANGO_DEPENDENCIES = [
    "django>=4.2",
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

DJANGO_DIRECTORIES = [
    "bot/handlers",
    "bot/middlewares",
    "bot/filters",
    "bot/keyboards",
    "bot/states",
    "django_app/models",
    "django_app/management/commands",
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
