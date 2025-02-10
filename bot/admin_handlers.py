from typing import Callable

import aiogram
import asyncpg

#Routers
from aiogram import Router
from aiogram.enums import ParseMode
#Filters
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from magic_filter import F
#Types
from aiogram.types.message import Message
from aiogram.types import User, CallbackQuery, InputMediaPhoto
from pyexpat.errors import messages

from bot.fsm import StatesData
#Project
from config import admin_ids, database_config
from bot.texts import *
from bot.keyboards import *


admin_router = Router()

class SettingsFilter(Filter):
    def __init__(self, states):
        self.states = states

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state in self.states


# @admin_router.callback_query(lambda callback: callback.data == "statistics_utils")
# async def view_statistics(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()
#     statistics = [await create_top_list()]
#     temporary_messages=[await callback.message.answer(stat) for stat in statistics]
#     await state.update_data(temporary_messages=temporary_messages)
#     main_message = await callback.message.answer(text="Это статистика вашего бота. Вернутся назад?",
#                                                  reply_markup=back_to_admin_keyboard)
#     await state.update_data(main_message=main_message)


@admin_router.callback_query(lambda callback: callback.data == "orders_list")
async def orders_list(callback: CallbackQuery, state:FSMContext):
    connection: asyncpg.Connection = await asyncpg.connect(**database_config)
    orders = await connection.fetch("SELECT * FROM orders "
                                    "INNER JOIN order_info ON orders.id = order_info.order_id "
                                    "INNER JOIN clients ON orders.client_id = clients.id "
                                    "WHERE status = 'НА РАССМОТРЕНИИ'")
    orders = [[order['order_id'], order] for order in orders]
    await state.update_data(orders=orders)
    await callback.message.delete()
    temporary_messages = [await callback.message.answer_document(caption=await create_order_list(pair[0], pair[1]),
                                                                 document=pair[1]['file_id'],
                                                                 reply_markup=await create_order_keyboard(pair[0]),
                                                                 parse_mode=ParseMode.MARKDOWN)
                                                                 if orders else await callback.messsage.answer (text="Сейчас заказов нет. Заходите позднее!")
                                                                 for pair in orders]
    main_message = await callback.message.answer(text=f"Вернуться назад?", reply_markup=back_to_admin_keyboard)
    await state.update_data(temporary_messages=temporary_messages, main_message=main_message)


@admin_router.callback_query(lambda callback: callback.data == "back_admin_panel")
async def back_to_admin(callback: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    for message in data['temporary_messages']:
        try:
            await message.delete()
        except:
            pass
    await callback.message.edit_media(media=InputMediaPhoto(media=image_admin_panel, caption = text_admin_panel),
                                      reply_markup=keyboard_admin_panel)


@admin_router.callback_query(lambda callback: callback.data.startswith("confirm_order"))
async def after_order_confirm(callback: CallbackQuery, state: FSMContext):
    order_num = int(callback.data.split("_")[-1])
    orders_settings_dict = {
        "nozzle_temperature": None,
        "table_temperature": None,
        "printing_speed": None,
        "layer_thickness": None,
        "current_ord_num": order_num
    }
    await state.update_data(orders_settings_dict=orders_settings_dict)
    orders_list_msgs = (await state.get_data())['temporary_messages']

    for message in orders_list_msgs:
        try:
            await message.delete()
        except:
            pass

    main_message: Message = ((await state.get_data())['main_message'])
    await main_message.edit_text(text = await order_settings(order_num, state),
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=await gen_settings_keyboard(state))


@admin_router.callback_query(lambda callback: callback.data.startswith("decline_order_"))
async def remove_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    connection: asyncpg.Connection = await asyncpg.connect(**database_config)
    order_id = int(callback.data.split("_")[-1])
    print(order_id)
    await connection.execute("DELETE FROM orders "
                             f"WHERE id = {order_id}")


@admin_router.callback_query(lambda callback: callback.data == "back_to_adm_orders")
async def back_to_admin_orders(callback: CallbackQuery, state: FSMContext):
        await orders_list(callback, state)


@admin_router.callback_query(lambda callback: callback.data in ["nozzle_temperature", "table_temperature","back_to_settings",
                                                             "printing_speed", "layer_thickness", "send_to_print",])
async def settings_questions(callback: CallbackQuery, state: FSMContext):
    if callback.data == "nozzle_temperature":
        await callback.message.edit_text(text="Напишите температуру сопла в цельсиях:",
                                            reply_markup=back_to_settings_keyboard)
        await state.set_state(StatesData.waiting_for_nozzle_temp)

    elif callback.data == "table_temperature":
        await callback.message.edit_text(text="Напишите температуру стола в цельсиях:",
                                            reply_markup=back_to_settings_keyboard)
        await state.set_state(StatesData.waiting_for_table_temp)

    elif callback.data == "printing_speed":
        await callback.message.edit_text(text="Напишите скорость печатающей головки в мм/c:",
                                            reply_markup=back_to_settings_keyboard)
        await state.set_state(StatesData.waiting_for_printing_speed)

    elif callback.data == "layer_thickness":
        await callback.message.edit_text(text="Напишите толщину слоя в мм:",
                                            reply_markup=back_to_settings_keyboard)
        await state.set_state(StatesData.waiting_for_layer_thickness)

    elif callback.data == "back_to_settings":
        order_num = (await state.get_data())['orders_settings_dict']['current_ord_num']
        await callback.message.edit_text(text=await order_settings(order_num, state),
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=await gen_settings_keyboard(state))

    elif callback.data == "send_to_print":
        order_num = (await state.get_data())['orders_settings_dict']['current_ord_num']
        connection = await asyncpg.connect(**database_config)
        await connection.execute(
            "UPDATE orders "
            "SET status = 'ОДОБРЕН' "
            f"WHERE id = {order_num}"
        )
        await orders_list(callback, state)

async def back_to_settings(message: Message, state: FSMContext):
    order_num = (await state.get_data())['orders_settings_dict']['current_ord_num']
    await message.edit_text(text=await order_settings(order_num, state),
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=await gen_settings_keyboard(state))


@admin_router.message(lambda message: message.text.isdigit(),
    SettingsFilter(states=[StatesData.waiting_for_nozzle_temp,
                                             StatesData.waiting_for_table_temp,
                                             StatesData.waiting_for_layer_thickness,
                                             StatesData.waiting_for_printing_speed]))
async def process_params(message: Message, state: FSMContext):
    user_input = float(message.text)
    current_state = await state.get_state()
    orders_settings_dict = (await state.get_data())['orders_settings_dict']
    main_message = (await state.get_data())['main_message']

    if current_state == StatesData.waiting_for_nozzle_temp:
        orders_settings_dict['nozzle_temperature'] = user_input
        await state.update_data(orders_settings_dict=orders_settings_dict)
        await message.delete()
        await back_to_settings(main_message, state)

    elif current_state == StatesData.waiting_for_table_temp:
        orders_settings_dict['table_temperature'] = user_input
        await state.update_data(orders_settings_dict=orders_settings_dict)
        await message.delete()
        await back_to_settings(main_message, state)

    elif current_state == StatesData.waiting_for_layer_thickness:
        orders_settings_dict['layer_thickness'] = user_input
        await state.update_data(orders_settings_dict=orders_settings_dict)
        await message.delete()
        await back_to_settings(main_message, state)

    elif current_state == StatesData.waiting_for_printing_speed:
        orders_settings_dict['printing_speed'] = user_input
        await state.update_data(orders_settings_dict=orders_settings_dict)
        await message.delete()
        await back_to_settings(main_message, state)