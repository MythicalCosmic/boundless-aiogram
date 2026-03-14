def get_files(project_name: str, options: dict) -> dict:
    use_django = options.get("database") == "django"
    files = {}

    files["bot/handlers/__init__.py"] = '''from aiogram import Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.courses import router as courses_router
from bot.handlers.quiz import router as quiz_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(courses_router)
    dp.include_router(quiz_router)
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
        "Learn new skills with interactive courses and quizzes.\\n"
        "Track your progress and earn certificates.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>Learning Guide</b>\\n\\n"
        "/courses - Browse available courses\\n"
        "/quiz - Take a quiz\\n"
        "/progress - View your progress\\n"
        "/help - Show this help"
    )
'''

    files["bot/handlers/courses.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.courses_kb import courses_keyboard, lessons_keyboard

router = Router(name="courses")

COURSES = {
    "python": {
        "name": "Python Basics",
        "lessons": ["Variables & Types", "Control Flow", "Functions", "OOP Basics"],
    },
    "web": {
        "name": "Web Development",
        "lessons": ["HTML Basics", "CSS Styling", "JavaScript Intro", "APIs"],
    },
    "data": {
        "name": "Data Science",
        "lessons": ["Pandas", "Visualization", "Statistics", "ML Intro"],
    },
}


@router.message(Command("courses"))
async def list_courses(message: Message):
    text = "<b>Available Courses</b>\\n\\n"
    for key, course in COURSES.items():
        text += f"  {course['name']} ({len(course['lessons'])} lessons)\\n"
    await message.answer(text, reply_markup=courses_keyboard(COURSES))


@router.callback_query(F.data.startswith("course_"))
async def course_detail(callback: CallbackQuery):
    course_key = callback.data.split("_", 1)[1]
    course = COURSES.get(course_key)
    if not course:
        await callback.answer("Course not found")
        return

    text = f"<b>{course['name']}</b>\\n\\n<b>Lessons:</b>\\n"
    for i, lesson in enumerate(course["lessons"], 1):
        text += f"  {i}. {lesson}\\n"

    await callback.message.edit_text(text, reply_markup=lessons_keyboard(course_key, course["lessons"]))
    await callback.answer()


@router.callback_query(F.data.startswith("lesson_"))
async def lesson_view(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    course_key = parts[1]
    lesson_idx = int(parts[2])
    course = COURSES.get(course_key)
    if not course or lesson_idx >= len(course["lessons"]):
        await callback.answer("Lesson not found")
        return

    lesson_name = course["lessons"][lesson_idx]
    await callback.message.edit_text(
        f"<b>{course['name']}</b>\\n"
        f"Lesson: <b>{lesson_name}</b>\\n\\n"
        "This is where the lesson content would be displayed.\\n"
        "In production, load content from your database.\\n\\n"
        "<i>Lesson completed! Use /quiz to test your knowledge.</i>"
    )
    await callback.answer()
'''

    files["bot/handlers/quiz.py"] = '''from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.quiz import QuizState

router = Router(name="quiz")

QUIZ_QUESTIONS = [
    {
        "question": "What is Python?",
        "options": ["A snake", "A programming language", "A game", "A framework"],
        "correct": 1,
    },
    {
        "question": "What does HTML stand for?",
        "options": ["Hyper Tool Markup Language", "HyperText Markup Language",
                     "Home Text Making Language", "HyperText Machine Language"],
        "correct": 1,
    },
    {
        "question": "Which is used for version control?",
        "options": ["Python", "Docker", "Git", "Linux"],
        "correct": 2,
    },
]


@router.message(Command("quiz"))
async def start_quiz(message: Message, state: FSMContext):
    await state.update_data(question_idx=0, score=0)
    await state.set_state(QuizState.answering)
    await send_question(message, 0)


async def send_question(message: Message, idx: int):
    if idx >= len(QUIZ_QUESTIONS):
        return
    q = QUIZ_QUESTIONS[idx]
    text = f"<b>Question {idx + 1}/{len(QUIZ_QUESTIONS)}</b>\\n\\n{q['question']}\\n\\n"
    for i, opt in enumerate(q["options"]):
        text += f"  {i + 1}. {opt}\\n"
    text += "\\nReply with the number of your answer."
    await message.answer(text)


@router.message(QuizState.answering)
async def process_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data["question_idx"]
    score = data["score"]

    try:
        answer = int(message.text) - 1
    except (ValueError, TypeError):
        await message.answer("Please enter a number.")
        return

    q = QUIZ_QUESTIONS[idx]
    if answer == q["correct"]:
        score += 1
        await message.answer("Correct!")
    else:
        correct_answer = q["options"][q["correct"]]
        await message.answer(f"Wrong. The correct answer was: {correct_answer}")

    idx += 1
    if idx >= len(QUIZ_QUESTIONS):
        await state.clear()
        await message.answer(
            f"<b>Quiz Complete!</b>\\n\\n"
            f"Score: {score}/{len(QUIZ_QUESTIONS)}\\n\\n"
            f"{'Great job!' if score == len(QUIZ_QUESTIONS) else 'Keep learning!'}"
        )
    else:
        await state.update_data(question_idx=idx, score=score)
        await send_question(message, idx)
'''

    files["bot/keyboards/main_menu.py"] = '''from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Courses"), KeyboardButton(text="Quiz")],
            [KeyboardButton(text="My Progress"), KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
'''

    files["bot/keyboards/courses_kb.py"] = '''from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def courses_keyboard(courses: dict) -> InlineKeyboardMarkup:
    buttons = []
    for key, course in courses.items():
        buttons.append([
            InlineKeyboardButton(text=course["name"], callback_data=f"course_{key}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def lessons_keyboard(course_key: str, lessons: list) -> InlineKeyboardMarkup:
    buttons = []
    for i, lesson in enumerate(lessons):
        buttons.append([
            InlineKeyboardButton(text=lesson, callback_data=f"lesson_{course_key}_{i}")
        ])
    buttons.append([InlineKeyboardButton(text="<< Back to Courses", callback_data="courses_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
'''

    files["bot/states/quiz.py"] = '''from aiogram.fsm.state import State, StatesGroup


class QuizState(StatesGroup):
    answering = State()
'''

    if not use_django:
        files["database/models/__init__.py"] = '''from database.models.base import Base
from database.models.user import User
from database.models.course import Course, Lesson
from database.models.progress import UserProgress
'''
        files["database/models/course.py"] = '''from sqlalchemy import String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.base import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.sort_order")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    course = relationship("Course", back_populates="lessons")
'''
        files["database/models/progress.py"] = '''from datetime import datetime
from sqlalchemy import BigInteger, Integer, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.models.base import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
'''

    return files
