def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.ticket import router as ticket_router
from bot.handlers.faq import router as faq_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(ticket_router)
    dp.include_router(faq_router)
'''

    files["bot/handlers/start.py"] = '''from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>!\\n\\n"
        "Welcome to Customer Support.\\n"
        "Create tickets, browse FAQ, or chat with our team.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Support Commands</b>\\n\\n"
        "/new_ticket - Create a support ticket\\n"
        "/my_tickets - View your tickets\\n"
        "/faq - Frequently asked questions\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/ticket.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.ticket import TicketForm

router = Router(name="ticket")


@router.message(Command("new_ticket"))
async def start_ticket(message: Message, state: FSMContext):
    await state.set_state(TicketForm.subject)
    await message.answer("Enter the <b>subject</b> of your issue:")


@router.message(TicketForm.subject)
async def process_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(TicketForm.category)
    await message.answer(
        "Select a <b>category</b>:\\n\\n"
        "1. Technical Issue\\n"
        "2. Billing\\n"
        "3. Account\\n"
        "4. Feature Request\\n"
        "5. Other"
    )


@router.message(TicketForm.category)
async def process_category(message: Message, state: FSMContext):
    categories = {"1": "Technical", "2": "Billing", "3": "Account", "4": "Feature Request", "5": "Other"}
    category = categories.get(message.text, message.text)
    await state.update_data(category=category)
    await state.set_state(TicketForm.description)
    await message.answer("Describe your issue in detail:")


@router.message(TicketForm.description)
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()
    data["description"] = message.text
    await state.clear()

    await message.answer(
        "<b>Ticket Created!</b>\\n\\n"
        f"Subject: {data['subject']}\\n"
        f"Category: {data['category']}\\n"
        f"Description: {data['description']}\\n\\n"
        "Ticket ID: #001\\n"
        "Status: Open\\n\\n"
        "Our team will respond as soon as possible."
    )


@router.message(Command("my_tickets"))
async def my_tickets(message: Message):
    await message.answer(
        "<b>Your Tickets</b>\\n\\n"
        "No open tickets.\\n"
        "Use /new_ticket to create one."
    )
'''

    files["bot/handlers/faq.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.faq_kb import faq_keyboard

router = Router(name="faq")

FAQ_ITEMS = {
    "hours": {
        "question": "What are your working hours?",
        "answer": "We are available Monday to Friday, 9:00 AM - 6:00 PM.",
    },
    "refund": {
        "question": "How do I request a refund?",
        "answer": "Contact support with your order number. Refunds are processed within 5-7 business days.",
    },
    "shipping": {
        "question": "What are the shipping options?",
        "answer": "We offer standard (5-7 days) and express (1-2 days) shipping.",
    },
    "account": {
        "question": "How do I reset my password?",
        "answer": "Go to Settings > Security > Reset Password, or contact support.",
    },
}


@router.message(Command("faq"))
async def show_faq(message: Message):
    text = "<b>Frequently Asked Questions</b>\\n\\nSelect a topic:"
    await message.answer(text, reply_markup=faq_keyboard(FAQ_ITEMS))


@router.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: CallbackQuery):
    key = callback.data.split("_", 1)[1]
    item = FAQ_ITEMS.get(key)
    if not item:
        await callback.answer("Not found")
        return
    await callback.message.edit_text(
        f"<b>Q: {item['question']}</b>\\n\\n"
        f"A: {item['answer']}\\n\\n"
        "Was this helpful? If not, use /new_ticket to contact us.",
        reply_markup=faq_keyboard(FAQ_ITEMS),
    )
    await callback.answer()
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="New Ticket"), KeyboardButton(text="My Tickets")],
            [KeyboardButton(text="FAQ"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/faq_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def faq_keyboard(faq_items: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, item in faq_items.items():
        buttons.append([
            InlineKeyboardButton(text=item["question"], callback_data=f"faq_{key}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/ticket.py"] = '''from aiogram.fsm.state import State, StatesGroup


class TicketForm(StatesGroup):
    subject = State()
    category = State()
    description = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.ticket import Ticket, TicketMessage
'''
        files["database/models/ticket.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    subject: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    messages = relationship("TicketMessage", back_populates="ticket", order_by="TicketMessage.created_at")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    sender_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str] = mapped_column(Text)
    is_staff: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ticket = relationship("Ticket", back_populates="messages")
'''

    return files
