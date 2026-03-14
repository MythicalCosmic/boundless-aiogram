def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.shipment import router as shipment_router
from bot.handlers.tracking import router as tracking_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(shipment_router)
    dp.include_router(tracking_router)
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
        "Create shipments, track packages, and manage deliveries.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Delivery Commands</b>\\n\\n"
        "/new_shipment - Create a new shipment\\n"
        "/track - Track a package\\n"
        "/my_shipments - View your shipments\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/shipment.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.shipment import ShipmentForm

router = Router(name="shipment")


@router.message(Command("new_shipment"))
async def start_shipment(message: Message, state: FSMContext):
    await state.set_state(ShipmentForm.sender_address)
    await message.answer("Enter the <b>pickup address</b>:")


@router.message(ShipmentForm.sender_address)
async def process_sender(message: Message, state: FSMContext):
    await state.update_data(sender_address=message.text)
    await state.set_state(ShipmentForm.receiver_address)
    await message.answer("Enter the <b>delivery address</b>:")


@router.message(ShipmentForm.receiver_address)
async def process_receiver(message: Message, state: FSMContext):
    await state.update_data(receiver_address=message.text)
    await state.set_state(ShipmentForm.weight)
    await message.answer("Enter package <b>weight</b> in kg:")


@router.message(ShipmentForm.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(ShipmentForm.description)
    await message.answer("Briefly describe the package contents:")


@router.message(ShipmentForm.description)
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()
    data["description"] = message.text
    await state.clear()

    await message.answer(
        "<b>Shipment Created!</b>\\n\\n"
        f"From: {data['sender_address']}\\n"
        f"To: {data['receiver_address']}\\n"
        f"Weight: {data['weight']} kg\\n"
        f"Contents: {data['description']}\\n\\n"
        "Tracking ID: TRK-00001\\n"
        "Status: Pending Pickup\\n\\n"
        "Use /track TRK-00001 to check status."
    )
'''

    files["bot/handlers/tracking.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="tracking")


@router.message(Command("track"))
async def track_package(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /track <tracking_id>\\n\\nExample: /track TRK-00001")
        return

    tracking_id = parts[1].strip()
    await message.answer(
        f"<b>Tracking: {tracking_id}</b>\\n\\n"
        "Status: In Transit\\n\\n"
        "Timeline:\\n"
        "  [+] Package received\\n"
        "  [+] Picked up by courier\\n"
        "  [*] In transit\\n"
        "  [ ] Out for delivery\\n"
        "  [ ] Delivered\\n\\n"
        "<i>Connect to your database for real tracking data.</i>"
    )


@router.message(Command("my_shipments"))
async def my_shipments(message: Message):
    await message.answer(
        "<b>Your Shipments</b>\\n\\n"
        "No shipments found.\\n"
        "Use /new_shipment to create one."
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="New Shipment"), KeyboardButton(text="Track")],
            [KeyboardButton(text="My Shipments"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/states/shipment.py"] = '''from aiogram.fsm.state import State, StatesGroup


class ShipmentForm(StatesGroup):
    sender_address = State()
    receiver_address = State()
    weight = State()
    description = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.package import Package
from database.models.tracking import TrackingUpdate
'''
        files["database/models/package.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Float, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_id: Mapped[str] = mapped_column(String(50), unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    sender_address: Mapped[str] = mapped_column(String(500))
    receiver_address: Mapped[str] = mapped_column(String(500))
    weight_kg: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    updates = relationship("TrackingUpdate", back_populates="package", order_by="TrackingUpdate.created_at")
'''
        files["database/models/tracking.py"] = '''from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class TrackingUpdate(Base):
    __tablename__ = "tracking_updates"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.id"))
    status: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(255), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    package = relationship("Package", back_populates="updates")
'''

    return files
