#Телеграм API
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

#Импорты из проекта
from bot.fsm import StatesData
from bot.texts import *
from bot.keyboards import gen_start_menu_kb

user_router = Router()


@user_router.message(CommandStart)
async def start_menu(message: Message, state: FSMContext):
    await state.set_state(StatesData.none_state)
    await message.answer(text=welcome_text,
                         reply_markup=await gen_start_menu_kb(user_id=message.from_user.id))

