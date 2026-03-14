def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.services import router as services_router
from bot.handlers.booking import router as booking_router
from bot.handlers.my_bookings import router as my_bookings_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(services_router)
    dp.include_router(booking_router)
    dp.include_router(my_bookings_router)
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
        "Book appointments quickly and easily.\\n"
        "Browse available services and pick a time that works for you.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Booking Guide</b>\\n\\n"
        "/services - View available services\\n"
        "/book - Start a new booking\\n"
        "/my_bookings - View your appointments\\n"
        "/cancel - Cancel a booking\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/services.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.services_kb import services_keyboard

router = Router(name="services")

SERVICES = [
    {"id": "haircut", "name": "Haircut", "duration": "30 min", "price": 25},
    {"id": "massage", "name": "Massage Therapy", "duration": "60 min", "price": 60},
    {"id": "dental", "name": "Dental Checkup", "duration": "45 min", "price": 80},
    {"id": "consult", "name": "Consultation", "duration": "30 min", "price": 40},
    {"id": "training", "name": "Personal Training", "duration": "60 min", "price": 50},
]


@router.message(Command("services"))
async def list_services(message: Message):
    text = "<b>Available Services</b>\\n\\n"
    for s in SERVICES:
        text += f"  {s['name']} -- {s['duration']} -- ${s['price']}\\n"
    text += "\\nSelect a service to book:"
    await message.answer(text, reply_markup=services_keyboard(SERVICES))


@router.callback_query(F.data.startswith("svc_"))
async def service_detail(callback: CallbackQuery):
    svc_id = callback.data.split("_", 1)[1]
    service = next((s for s in SERVICES if s["id"] == svc_id), None)
    if not service:
        await callback.answer("Service not found")
        return
    await callback.message.edit_text(
        f"<b>{service['name']}</b>\\n\\n"
        f"Duration: {service['duration']}\\n"
        f"Price: ${service['price']}\\n\\n"
        "Use /book to schedule this service."
    )
    await callback.answer()
'''

    files["bot/handlers/booking.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.booking import BookingForm

router = Router(name="booking")


@router.message(Command("book"))
async def start_booking(message: Message, state: FSMContext):
    await state.set_state(BookingForm.service)
    await message.answer(
        "Which service would you like to book?\\n"
        "(haircut / massage / dental / consult / training)"
    )


@router.message(BookingForm.service)
async def process_service(message: Message, state: FSMContext):
    await state.update_data(service=message.text)
    await state.set_state(BookingForm.date)
    await message.answer("Enter preferred <b>date</b> (e.g. 2025-03-20):")


@router.message(BookingForm.date)
async def process_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(BookingForm.time)
    await message.answer("Enter preferred <b>time</b> (e.g. 14:00):")


@router.message(BookingForm.time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(BookingForm.name)
    await message.answer("Enter your <b>full name</b>:")


@router.message(BookingForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookingForm.phone)
    await message.answer("Enter your <b>phone number</b>:")


@router.message(BookingForm.phone)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    data["phone"] = message.text
    await state.clear()

    await message.answer(
        "<b>Booking Confirmed!</b>\\n\\n"
        f"Service: {data['service']}\\n"
        f"Date: {data['date']}\\n"
        f"Time: {data['time']}\\n"
        f"Name: {data['name']}\\n"
        f"Phone: {data['phone']}\\n\\n"
        "We will send you a reminder before your appointment."
    )
'''

    files["bot/handlers/my_bookings.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="my_bookings")


@router.message(Command("my_bookings"))
async def my_bookings(message: Message):
    await message.answer(
        "<b>Your Bookings</b>\\n\\n"
        "No upcoming bookings found.\\n\\n"
        "Use /book to schedule a new appointment."
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Services"), KeyboardButton(text="Book Now")],
            [KeyboardButton(text="My Bookings"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/services_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def services_keyboard(services: list) -> InlineKeyboardMarkup:
    buttons = []
    for s in services:
        buttons.append([
            InlineKeyboardButton(
                text=f"{s['name']} -- ${s['price']}",
                callback_data=f"svc_{s['id']}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/booking.py"] = '''from aiogram.fsm.state import State, StatesGroup


class BookingForm(StatesGroup):
    service = State()
    date = State()
    time = State()
    name = State()
    phone = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.service import Service
from database.models.booking import Booking
'''
        files["database/models/service.py"] = '''from sqlalchemy import String, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
'''
        files["database/models/booking.py"] = '''from datetime import datetime, date, time
from sqlalchemy import BigInteger, String, Date, Time, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    booking_time: Mapped[time] = mapped_column(Time)
    client_name: Mapped[str] = mapped_column(String(255))
    client_phone: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''

    return files
