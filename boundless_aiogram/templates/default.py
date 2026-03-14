def get_files(project_name: str, options: dict) -> dict:
    return {
        "bot/handlers/__init__.py": '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.echo import router as echo_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(echo_router)
''',
        "bot/handlers/start.py": '''from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome, <b>{message.from_user.full_name}</b>!\\n\\n"
        "I am an echo bot. Send me any message and I will repeat it back.\\n\\n"
        "Commands:\\n"
        "/start - Start the bot\\n"
        "/help - Show help\\n"
        "/about - About this bot",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Help</b>\\n\\n"
        "Just send me any text message and I will echo it back to you.\\n"
        "This is a starter template -- customize it to build your bot!"
    )


@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer(
        "<b>About</b>\\n\\n"
        f"Project: <code>{project_name}</code>\\n"
        "Built with Boundless + Aiogram 3.x"
    )
'''.replace("{project_name}", project_name),
        "bot/handlers/echo.py": '''from aiogram import Router
from aiogram.types import Message

router = Router(name="echo")


@router.message()
async def echo_handler(message: Message):
    if message.text:
        await message.answer(message.text)
    else:
        await message.answer("I can only echo text messages.")
''',
        "bot/keyboards/main_menu.py": '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Help"), KeyboardButton(text="About")],
        ],
        resize_keyboard=True,
    )
''',
    }
