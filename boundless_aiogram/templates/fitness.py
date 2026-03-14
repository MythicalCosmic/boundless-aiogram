def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.workouts import router as workouts_router
from bot.handlers.log import router as log_router
from bot.handlers.progress import router as progress_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(workouts_router)
    dp.include_router(log_router)
    dp.include_router(progress_router)
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
        "Your personal fitness assistant.\\n"
        "Browse workouts, log exercises, and track your progress.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Fitness Bot Commands</b>\\n\\n"
        "/workouts - Browse workout plans\\n"
        "/log - Log a workout\\n"
        "/progress - View your stats\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/workouts.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.workouts_kb import workout_types_keyboard

router = Router(name="workouts")

WORKOUTS = {
    "strength": {
        "name": "Strength Training",
        "exercises": [
            "Bench Press - 4x8",
            "Squats - 4x10",
            "Deadlift - 3x8",
            "Overhead Press - 3x10",
        ],
    },
    "cardio": {
        "name": "Cardio",
        "exercises": [
            "Running - 30 min",
            "Jump Rope - 15 min",
            "Cycling - 45 min",
            "HIIT - 20 min",
        ],
    },
    "flexibility": {
        "name": "Flexibility",
        "exercises": [
            "Yoga Flow - 30 min",
            "Stretching Routine - 20 min",
            "Pilates - 30 min",
            "Foam Rolling - 15 min",
        ],
    },
    "bodyweight": {
        "name": "Bodyweight",
        "exercises": [
            "Push-ups - 4x20",
            "Pull-ups - 4x10",
            "Planks - 3x60s",
            "Lunges - 3x15",
            "Burpees - 3x12",
        ],
    },
}


@router.message(Command("workouts"))
async def list_workouts(message: Message):
    text = "<b>Workout Plans</b>\\n\\nSelect a workout type:"
    await message.answer(text, reply_markup=workout_types_keyboard(WORKOUTS))


@router.callback_query(F.data.startswith("workout_"))
async def workout_detail(callback: CallbackQuery):
    key = callback.data.split("_", 1)[1]
    workout = WORKOUTS.get(key)
    if not workout:
        await callback.answer("Not found")
        return

    text = f"<b>{workout['name']}</b>\\n\\n"
    for ex in workout["exercises"]:
        text += f"  - {ex}\\n"
    text += "\\nUse /log to record your workout."

    await callback.message.edit_text(text, reply_markup=workout_types_keyboard(WORKOUTS))
    await callback.answer()
'''

    files["bot/handlers/log.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.workout import LogForm

router = Router(name="log")


@router.message(Command("log"))
async def start_log(message: Message, state: FSMContext):
    await state.set_state(LogForm.exercise)
    await message.answer("What <b>exercise</b> did you do?")


@router.message(LogForm.exercise)
async def process_exercise(message: Message, state: FSMContext):
    await state.update_data(exercise=message.text)
    await state.set_state(LogForm.sets)
    await message.answer("How many <b>sets</b>?")


@router.message(LogForm.sets)
async def process_sets(message: Message, state: FSMContext):
    await state.update_data(sets=message.text)
    await state.set_state(LogForm.reps)
    await message.answer("How many <b>reps</b> per set? (or duration in minutes)")


@router.message(LogForm.reps)
async def process_reps(message: Message, state: FSMContext):
    await state.update_data(reps=message.text)
    await state.set_state(LogForm.weight)
    await message.answer("Weight used in kg? (or type /skip for bodyweight)")


@router.message(LogForm.weight)
async def process_weight(message: Message, state: FSMContext):
    data = await state.get_data()
    weight = "bodyweight" if message.text == "/skip" else message.text
    await state.clear()

    await message.answer(
        "<b>Workout Logged!</b>\\n\\n"
        f"Exercise: {data['exercise']}\\n"
        f"Sets: {data['sets']}\\n"
        f"Reps: {data['reps']}\\n"
        f"Weight: {weight}\\n\\n"
        "Keep up the good work! Use /progress to see your stats."
    )
'''

    files["bot/handlers/progress.py"] = '''from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="progress")


@router.message(Command("progress"))
async def show_progress(message: Message):
    await message.answer(
        "<b>Your Fitness Stats</b>\\n\\n"
        "Total workouts: 0\\n"
        "This week: 0\\n"
        "Streak: 0 days\\n\\n"
        "<i>Connect to your database to track real progress.</i>\\n\\n"
        "Keep logging your workouts with /log!"
    )
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Workouts"), KeyboardButton(text="Log Workout")],
            [KeyboardButton(text="Progress"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/workouts_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def workout_types_keyboard(workouts: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, w in workouts.items():
        buttons.append([InlineKeyboardButton(text=w["name"], callback_data=f"workout_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/workout.py"] = '''from aiogram.fsm.state import State, StatesGroup


class LogForm(StatesGroup):
    exercise = State()
    sets = State()
    reps = State()
    weight = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.workout import WorkoutLog
'''
        files["database/models/workout.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    exercise: Mapped[str] = mapped_column(String(255))
    sets: Mapped[int] = mapped_column(Integer, default=0)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    weight_kg: Mapped[float] = mapped_column(Float, default=0)
    duration_min: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''

    return files
