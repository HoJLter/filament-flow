#Телеграм API
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, User
#Асинхронность
import asyncio
#Импорты из проекта
from bot.fsm import StatesData
from bot.texts import *
from bot.keyboards import keyboard_start_gen, keyboard_back_to_start, keyboard_order_menu, keyboard_admin_panel, \
    keyboard_back_to_order

user_router = Router()


@user_router.message(Command("start", prefix="/"))
async def welcome_command(message: Message, state: FSMContext):
    await state.set_state(StatesData.none_state)
    await message.delete()
    user = message.from_user
    await state.update_data(user=user)
    master_msg = await message.answer_photo(photo=image_welcome , caption=text_welcome,
                                            reply_markup=await keyboard_start_gen(user_id=message.from_user.id))
    try:
        await (await state.get_data())["master_msg"].delete()
    except:
        pass
    await state.update_data(master_msg=master_msg)


@user_router.callback_query(lambda callback: callback.data in ['create_order',
                                                               'admin_panel',
                                                               'info',
                                                               'back_to_order_menu'])
async def start_menu(callback:CallbackQuery, state: FSMContext):
    if callback.data in ["create_order", 'back_to_order_menu']:
        await state.update_data(order_parameters=None)
        await callback.message.edit_media(media=InputMediaPhoto(media=image_order_menu,
                                                                caption=await text_order_menu_gen(state)),
                                          reply_markup=keyboard_order_menu)
    elif callback.data == "admin_panel":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_admin_panel),
                                          reply_markup=keyboard_admin_panel)
    elif callback.data == "info":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_info,
                                                                caption=text_info),
                                          reply_markup=keyboard_back_to_start)


@user_router.callback_query(lambda callback: callback.data == "back_to_start_menu")
async def back_to_start_menu(callback: CallbackQuery, state: FSMContext):
    user: User = (await state.get_data())['user']
    await callback.message.edit_media(media=InputMediaPhoto(media=image_welcome, caption=text_welcome),
                                            reply_markup=await keyboard_start_gen(user_id=user.id))


@user_router.callback_query(lambda callback: callback.data in ['order_name',
                                                               'reference',
                                                               'mail_index',
                                                               'send_file',
                                                               'complete_button'])
async def order_parameters(callback: CallbackQuery, state: FSMContext):
    if callback.data == "order_name":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_welcome, caption="Укажите наименование заказа:"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_order_name)

    elif callback.data == "reference":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_welcome, caption="Укажите техническое задание:"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_references)

    elif callback.data == "mail_index":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_welcome, caption="Укажите почтовый индекс Почты России:"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_index)

    elif callback.data == "send_file":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_welcome, caption="Отправьте .stl модель для печати"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_file)

    elif callback.data == "complete_button":
        temp_message = await callback.message.answer(text = text_order_edit_complete)
        await asyncio.sleep(4)
        await temp_message.delete()



@user_router.message(StatesData.waiting_for_file or
                     StatesData.waiting_for_index or
                     StatesData.waiting_for_references or
                     StatesData.waiting_for_order_name)
async def set_params(message: Message, state:FSMContext):
    current_state = await state.get_state()
    print(current_state)
    if current_state == StatesData.waiting_for_file:
        print("file")
    elif current_state == StatesData.waiting_for_index:
        print("index")


@user_router.message(F.photo)
async def photo_test(message: Message):
    print(message.photo[-1])


@user_router.message(StatesData.none_state)
async def delete_useless(message:Message):
    await message.delete()