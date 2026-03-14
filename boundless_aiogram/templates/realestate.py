def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.search import router as search_router
from bot.handlers.inquiry import router as inquiry_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(inquiry_router)
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
        "Find your perfect property.\\n"
        "Search listings, get details, and submit inquiries.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Commands</b>\\n\\n"
        "/search - Search properties\\n"
        "/listings - View all listings\\n"
        "/inquiry - Submit an inquiry\\n"
        "/saved - Your saved searches\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/search.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.search import PropertySearch
from bot.keyboards.search_kb import property_type_keyboard

router = Router(name="search")


@router.message(Command("search"))
async def start_search(message: Message, state: FSMContext):
    await state.set_state(PropertySearch.property_type)
    await message.answer(
        "What type of property are you looking for?",
        reply_markup=property_type_keyboard(),
    )


@router.message(PropertySearch.property_type)
async def process_type(message: Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await state.set_state(PropertySearch.location)
    await message.answer("Enter the <b>location</b> or area:")


@router.message(PropertySearch.location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(PropertySearch.price_range)
    await message.answer(
        "Enter your <b>budget range</b> (e.g. 50000-100000):"
    )


@router.message(PropertySearch.price_range)
async def process_price(message: Message, state: FSMContext):
    await state.update_data(price_range=message.text)
    await state.set_state(PropertySearch.rooms)
    await message.answer("How many <b>rooms</b> do you need? (1-5+)")


@router.message(PropertySearch.rooms)
async def process_rooms(message: Message, state: FSMContext):
    data = await state.get_data()
    data["rooms"] = message.text
    await state.clear()

    await message.answer(
        "<b>Search Results</b>\\n\\n"
        f"Type: {data['property_type']}\\n"
        f"Location: {data['location']}\\n"
        f"Budget: {data['price_range']}\\n"
        f"Rooms: {data['rooms']}\\n\\n"
        "No properties match your criteria yet.\\n"
        "<i>Connect to your database to show real listings.</i>\\n\\n"
        "Use /inquiry to contact our agents."
    )
'''

    files["bot/handlers/inquiry.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.search import InquiryForm

router = Router(name="inquiry")


@router.message(Command("inquiry"))
async def start_inquiry(message: Message, state: FSMContext):
    await state.set_state(InquiryForm.name)
    await message.answer("Enter your <b>full name</b>:")


@router.message(InquiryForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(InquiryForm.phone)
    await message.answer("Enter your <b>phone number</b>:")


@router.message(InquiryForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(InquiryForm.message)
    await message.answer("Describe what you are looking for:")


@router.message(InquiryForm.message)
async def process_message(message: Message, state: FSMContext):
    data = await state.get_data()
    data["message"] = message.text
    await state.clear()

    await message.answer(
        "<b>Inquiry Submitted!</b>\\n\\n"
        f"Name: {data['name']}\\n"
        f"Phone: {data['phone']}\\n"
        f"Message: {data['message']}\\n\\n"
        "An agent will contact you shortly."
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Search"), KeyboardButton(text="Listings")],
            [KeyboardButton(text="Inquiry"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/search_kb.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def property_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Apartment"), KeyboardButton(text="House")],
            [KeyboardButton(text="Office"), KeyboardButton(text="Land")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
'''

    files["bot/states/search.py"] = '''from aiogram.fsm.state import State, StatesGroup


class PropertySearch(StatesGroup):
    property_type = State()
    location = State()
    price_range = State()
    rooms = State()


class InquiryForm(StatesGroup):
    name = State()
    phone = State()
    message = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.property import Property
from database.models.inquiry import Inquiry
'''
        files["database/models/property.py"] = '''from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    property_type: Mapped[str] = mapped_column(String(50))
    location: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    rooms: Mapped[int] = mapped_column(Integer)
    area_sqm: Mapped[float] = mapped_column(Float, default=0)
    description: Mapped[str] = mapped_column(Text, default="")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''
        files["database/models/inquiry.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Inquiry(Base):
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    property_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''

    return files
