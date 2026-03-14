def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.vacancies import router as vacancy_router
from bot.handlers.application import router as application_router
from bot.handlers.admin_hr import router as admin_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(vacancy_router)
    dp.include_router(application_router)
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
        "I am the HR assistant bot.\\n\\n"
        "Browse open vacancies, submit applications, "
        "and track your application status -- all right here.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Available Commands</b>\\n\\n"
        "/start - Main menu\\n"
        "/vacancies - Browse open positions\\n"
        "/apply - Submit an application\\n"
        "/my_applications - Check your application status\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/vacancies.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.vacancy_kb import vacancy_list_keyboard, vacancy_detail_keyboard

router = Router(name="vacancies")


@router.message(Command("vacancies"))
async def list_vacancies(message: Message):
    # Replace with database query in production
    await message.answer(
        "<b>Open Positions</b>\\n\\n"
        "Select a vacancy to see details:",
        reply_markup=vacancy_list_keyboard(),
    )


@router.callback_query(F.data.startswith("vacancy_"))
async def vacancy_detail(callback: CallbackQuery):
    vacancy_id = callback.data.split("_")[1]
    await callback.message.edit_text(
        f"<b>Position #{vacancy_id}</b>\\n\\n"
        "Department: Engineering\\n"
        "Location: Remote\\n"
        "Type: Full-time\\n\\n"
        "Requirements:\\n"
        "- 2+ years experience\\n"
        "- Team player\\n\\n"
        "Click Apply to submit your application.",
        reply_markup=vacancy_detail_keyboard(vacancy_id),
    )
    await callback.answer()
'''

    files["bot/handlers/application.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.application import ApplicationForm

router = Router(name="application")


@router.message(Command("apply"))
async def start_application(message: Message, state: FSMContext):
    await state.set_state(ApplicationForm.full_name)
    await message.answer("Let's start your application.\\n\\nPlease enter your <b>full name</b>:")


@router.callback_query(F.data.startswith("apply_"))
async def apply_from_vacancy(callback: CallbackQuery, state: FSMContext):
    vacancy_id = callback.data.split("_")[1]
    await state.update_data(vacancy_id=vacancy_id)
    await state.set_state(ApplicationForm.full_name)
    await callback.message.answer("Please enter your <b>full name</b>:")
    await callback.answer()


@router.message(ApplicationForm.full_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ApplicationForm.phone)
    await message.answer("Enter your <b>phone number</b>:")


@router.message(ApplicationForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(ApplicationForm.experience)
    await message.answer("Briefly describe your <b>experience</b>:")


@router.message(ApplicationForm.experience)
async def process_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(ApplicationForm.resume)
    await message.answer(
        "Please upload your <b>resume</b> as a document.\\n"
        "Or type /skip to continue without a resume."
    )


@router.message(ApplicationForm.resume)
async def process_resume(message: Message, state: FSMContext):
    if message.document:
        await state.update_data(resume_file_id=message.document.file_id)
    elif message.text and message.text.lower() == "/skip":
        await state.update_data(resume_file_id=None)
    else:
        await message.answer("Please send a document or type /skip.")
        return

    data = await state.get_data()
    await state.clear()

    await message.answer(
        "<b>Application Submitted!</b>\\n\\n"
        f"Name: {data['full_name']}\\n"
        f"Phone: {data['phone']}\\n"
        f"Experience: {data['experience']}\\n"
        f"Resume: {'Attached' if data.get('resume_file_id') else 'Not provided'}\\n\\n"
        "We will review your application and get back to you. Good luck!"
    )
'''

    files["bot/handlers/admin_hr.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from core.config import settings

router = Router(name="admin_hr")


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != settings.ADMIN_ID:
        return
    await message.answer(
        "<b>HR Admin Panel</b>\\n\\n"
        "/add_vacancy - Create new vacancy\\n"
        "/applications - View all applications\\n"
        "/stats - Recruitment statistics"
    )


@router.message(Command("stats"))
async def hr_stats(message: Message):
    if message.from_user.id != settings.ADMIN_ID:
        return
    await message.answer(
        "<b>Recruitment Statistics</b>\\n\\n"
        "Open vacancies: 0\\n"
        "Total applications: 0\\n"
        "Pending review: 0\\n"
        "Hired this month: 0\\n\\n"
        "<i>Connect to your database to see real data.</i>"
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Vacancies"), KeyboardButton(text="Apply")],
            [KeyboardButton(text="My Applications"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/vacancy_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def vacancy_list_keyboard() -> InlineKeyboardMarkup:
    # In production, build this dynamically from database
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Senior Python Developer", callback_data="vacancy_1")],
        [InlineKeyboardButton(text="Project Manager", callback_data="vacancy_2")],
        [InlineKeyboardButton(text="UI/UX Designer", callback_data="vacancy_3")],
    ])


def vacancy_detail_keyboard(vacancy_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Apply Now", callback_data=f"apply_{vacancy_id}")],
        [InlineKeyboardButton(text="<< Back to List", callback_data="vacancies_back")],
    ])
'''

    files["bot/states/application.py"] = '''from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    full_name = State()
    phone = State()
    experience = State()
    resume = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.vacancy import Vacancy
from database.models.application import Application
'''
        files["database/models/vacancy.py"] = '''from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    department: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255), default="Remote")
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    applications = relationship("Application", back_populates="vacancy")

    def __repr__(self) -> str:
        return f"<Vacancy(id={self.id}, title={self.title})>"
'''
        files["database/models/application.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"))
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))
    experience: Mapped[str] = mapped_column(Text)
    resume_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    vacancy = relationship("Vacancy", back_populates="applications")

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, user={self.full_name}, status={self.status})>"
'''
    else:
        files["django_app/models/__init__.py"] = '''from django_app.models.user import BotUser
from django_app.models.vacancy import Vacancy
from django_app.models.application import Application
'''
        files["django_app/models/vacancy.py"] = '''from django.db import models


class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Remote")
    description = models.TextField()
    requirements = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vacancies"
        verbose_name_plural = "vacancies"

    def __str__(self):
        return self.title
'''
        files["django_app/models/application.py"] = '''from django.db import models


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    user_id = models.BigIntegerField()
    vacancy = models.ForeignKey("Vacancy", on_delete=models.CASCADE, related_name="applications")
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    experience = models.TextField()
    resume_file_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "applications"

    def __str__(self):
        return f"{self.full_name} - {self.vacancy.title}"
'''

    return files
