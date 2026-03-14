def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.browse import router as browse_router
from bot.handlers.subscribe import router as subscribe_router
from bot.handlers.admin_post import router as admin_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(browse_router)
    dp.include_router(subscribe_router)
'''

    files["bot/handlers/start.py"] = '''from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome, <b>{message.from_user.full_name}</b>!\\n\\n"
        "Stay informed with the latest news and updates.\\n"
        "Subscribe to categories that interest you.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>News Bot Commands</b>\\n\\n"
        "/browse - Browse latest articles\\n"
        "/subscribe - Manage subscriptions\\n"
        "/categories - View categories\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/browse.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.news_kb import categories_keyboard

router = Router(name="browse")

CATEGORIES = {
    "tech": "Technology",
    "business": "Business",
    "sports": "Sports",
    "science": "Science",
    "entertainment": "Entertainment",
}


@router.message(Command("browse"))
@router.message(Command("categories"))
async def show_categories(message: Message):
    await message.answer(
        "<b>News Categories</b>\\n\\nSelect a category to browse:",
        reply_markup=categories_keyboard(CATEGORIES),
    )


@router.callback_query(F.data.startswith("newscat_"))
async def browse_category(callback: CallbackQuery):
    cat_key = callback.data.split("_", 1)[1]
    cat_name = CATEGORIES.get(cat_key, cat_key)
    await callback.message.edit_text(
        f"<b>{cat_name} News</b>\\n\\n"
        "No articles yet.\\n\\n"
        "<i>Connect to your database or news API to show real content.</i>"
    )
    await callback.answer()
'''

    files["bot/handlers/subscribe.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router(name="subscribe")


@router.message(Command("subscribe"))
async def manage_subscriptions(message: Message):
    await message.answer(
        "<b>Your Subscriptions</b>\\n\\n"
        "You are not subscribed to any categories yet.\\n\\n"
        "Use /categories to browse and subscribe."
    )
'''

    files["bot/handlers/admin_post.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.config import settings
from bot.states.post import PostForm

router = Router(name="admin_post")


@router.message(Command("post"))
async def start_post(message: Message, state: FSMContext):
    if message.from_user.id != settings.ADMIN_ID:
        return
    await state.set_state(PostForm.title)
    await message.answer("Enter article <b>title</b>:")


@router.message(PostForm.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(PostForm.content)
    await message.answer("Enter article <b>content</b>:")


@router.message(PostForm.content)
async def process_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await state.set_state(PostForm.category)
    await message.answer(
        "Select <b>category</b>:\\n"
        "tech / business / sports / science / entertainment"
    )


@router.message(PostForm.category)
async def process_category(message: Message, state: FSMContext):
    data = await state.get_data()
    data["category"] = message.text
    await state.clear()

    await message.answer(
        "<b>Article Published!</b>\\n\\n"
        f"Title: {data['title']}\\n"
        f"Category: {data['category']}\\n\\n"
        "Subscribers will be notified."
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Browse"), KeyboardButton(text="Categories")],
            [KeyboardButton(text="Subscriptions"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/news_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def categories_keyboard(categories: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, name in categories.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"newscat_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/post.py"] = '''from aiogram.fsm.state import State, StatesGroup


class PostForm(StatesGroup):
    title = State()
    content = State()
    category = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.article import Article
from database.models.subscription import Subscription
'''
        files["database/models/article.py"] = '''from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''
        files["database/models/subscription.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    category: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''

    return files
