def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.menu import router as menu_router
from bot.handlers.reservation import router as reservation_router
from bot.handlers.review import router as review_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(reservation_router)
    dp.include_router(review_router)
'''

    files["bot/handlers/start.py"] = '''from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Welcome to our restaurant, <b>{message.from_user.full_name}</b>!\\n\\n"
        "Browse our menu, make reservations, and leave reviews.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Restaurant Bot</b>\\n\\n"
        "/menu - View our menu\\n"
        "/reserve - Make a reservation\\n"
        "/review - Leave a review\\n"
        "/hours - Opening hours\\n"
        "/help - Show this help"
    )


@router.message(Command("hours"))
async def cmd_hours(message: Message):
    await message.answer(
        "<b>Opening Hours</b>\\n\\n"
        "Monday - Friday:  11:00 - 22:00\\n"
        "Saturday:          10:00 - 23:00\\n"
        "Sunday:            10:00 - 21:00\\n\\n"
        "Kitchen closes 1 hour before closing."
    )
'''

    files["bot/handlers/menu.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.menu_kb import menu_categories_keyboard

router = Router(name="menu")

MENU = {
    "starters": {
        "name": "Starters",
        "items": [
            {"name": "Caesar Salad", "price": 8.99},
            {"name": "Bruschetta", "price": 6.99},
            {"name": "Soup of the Day", "price": 5.99},
        ]
    },
    "mains": {
        "name": "Main Courses",
        "items": [
            {"name": "Grilled Salmon", "price": 18.99},
            {"name": "Beef Steak", "price": 22.99},
            {"name": "Pasta Carbonara", "price": 14.99},
            {"name": "Chicken Parmesan", "price": 16.99},
        ]
    },
    "desserts": {
        "name": "Desserts",
        "items": [
            {"name": "Tiramisu", "price": 7.99},
            {"name": "Chocolate Cake", "price": 6.99},
            {"name": "Ice Cream", "price": 4.99},
        ]
    },
}


@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer(
        "<b>Our Menu</b>\\n\\nSelect a category:",
        reply_markup=menu_categories_keyboard(MENU),
    )


@router.callback_query(F.data.startswith("restcat_"))
async def show_category(callback: CallbackQuery):
    cat_key = callback.data.split("_", 1)[1]
    category = MENU.get(cat_key)
    if not category:
        await callback.answer("Not found")
        return
    text = f"<b>{category['name']}</b>\\n\\n"
    for item in category["items"]:
        text += f"  {item['name']}  --  ${item['price']:.2f}\\n"
    await callback.message.edit_text(text, reply_markup=menu_categories_keyboard(MENU))
    await callback.answer()
'''

    files["bot/handlers/reservation.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.reservation import ReservationForm

router = Router(name="reservation")


@router.message(Command("reserve"))
async def start_reservation(message: Message, state: FSMContext):
    await state.set_state(ReservationForm.date)
    await message.answer("Enter reservation <b>date</b> (e.g. 2025-03-20):")


@router.message(ReservationForm.date)
async def process_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(ReservationForm.time)
    await message.answer("Enter reservation <b>time</b> (e.g. 19:00):")


@router.message(ReservationForm.time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(ReservationForm.guests)
    await message.answer("How many <b>guests</b>?")


@router.message(ReservationForm.guests)
async def process_guests(message: Message, state: FSMContext):
    await state.update_data(guests=message.text)
    await state.set_state(ReservationForm.name)
    await message.answer("Reservation under what <b>name</b>?")


@router.message(ReservationForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ReservationForm.phone)
    await message.answer("Enter your <b>phone number</b>:")


@router.message(ReservationForm.phone)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    data["phone"] = message.text
    await state.clear()

    await message.answer(
        "<b>Reservation Confirmed!</b>\\n\\n"
        f"Date: {data['date']}\\n"
        f"Time: {data['time']}\\n"
        f"Guests: {data['guests']}\\n"
        f"Name: {data['name']}\\n"
        f"Phone: {data['phone']}\\n\\n"
        "We look forward to seeing you!"
    )
'''

    files["bot/handlers/review.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.reservation import ReviewForm

router = Router(name="review")


@router.message(Command("review"))
async def start_review(message: Message, state: FSMContext):
    await state.set_state(ReviewForm.rating)
    await message.answer("Rate us from <b>1 to 5</b>:")


@router.message(ReviewForm.rating)
async def process_rating(message: Message, state: FSMContext):
    try:
        rating = int(message.text)
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        await message.answer("Please enter a number between 1 and 5.")
        return

    await state.update_data(rating=rating)
    await state.set_state(ReviewForm.comment)
    await message.answer("Leave a <b>comment</b> (or /skip):")


@router.message(ReviewForm.comment)
async def process_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    comment = "" if message.text == "/skip" else message.text
    await state.clear()

    stars = "*" * data["rating"] + "." * (5 - data["rating"])
    await message.answer(
        "<b>Thank you for your review!</b>\\n\\n"
        f"Rating: [{stars}] ({data['rating']}/5)\\n"
        f"Comment: {comment or 'No comment'}\\n\\n"
        "We appreciate your feedback!"
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Menu"), KeyboardButton(text="Reserve")],
            [KeyboardButton(text="Review"), KeyboardButton(text="Hours")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/menu_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def menu_categories_keyboard(menu: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, cat in menu.items():
        buttons.append([InlineKeyboardButton(text=cat["name"], callback_data=f"restcat_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/reservation.py"] = '''from aiogram.fsm.state import State, StatesGroup


class ReservationForm(StatesGroup):
    date = State()
    time = State()
    guests = State()
    name = State()
    phone = State()


class ReviewForm(StatesGroup):
    rating = State()
    comment = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.reservation import Reservation
from database.models.review import Review
'''
        files["database/models/reservation.py"] = '''from datetime import datetime, date, time
from sqlalchemy import BigInteger, String, Integer, Date, Time, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    reservation_date: Mapped[date] = mapped_column(Date)
    reservation_time: Mapped[time] = mapped_column(Time)
    guests: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''
        files["database/models/review.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''

    return files
