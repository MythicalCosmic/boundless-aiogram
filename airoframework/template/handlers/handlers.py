from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config.states import UserStates
from utils.utils import add_user, set_user_state

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    add_user(user_id, first_name, last_name, username)

    set_user_state(user_id, UserStates.start.state)


    await message.answer(f"Hello, {first_name}! Welcome to the bot.")

    await state.set_state(UserStates.start)
