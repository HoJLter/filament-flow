from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import admin_ids


async def keyboard_start_gen(user_id):
    create_order_button = InlineKeyboardButton(text = "Оформить заказ 🖋", callback_data="create_order")
    info_button = InlineKeyboardButton(text = "Информация 📖", callback_data="info")
    buttons = [[create_order_button],
               [info_button]]

    if user_id in admin_ids:
        admin_panel_button = InlineKeyboardButton(text = "Админ-панель 🔐", callback_data="admin_panel")
        buttons.append([admin_panel_button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


back_to_start_button = InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_start_menu")
keyboard_back_to_start = InlineKeyboardMarkup(inline_keyboard=[[back_to_start_button]])


name_button = InlineKeyboardButton(text="Название заказа 🔖", callback_data="order_name")
advices_button = InlineKeyboardButton(text="Техническое задание 🧩", callback_data="reference")
mail_index_button = InlineKeyboardButton(text="Почтовый индекс 📭", callback_data="mail_index")
send_file_button = InlineKeyboardButton(text="Файл 📁", callback_data="send_file")
complete_button = InlineKeyboardButton(text="Отправить ✅", callback_data="complete_button")
keyboard_order_menu = InlineKeyboardMarkup(inline_keyboard=[[name_button,
                                                            advices_button],
                                                            [mail_index_button,
                                                            send_file_button],
                                                            [complete_button],
                                                            [back_to_start_button]])


valid_index_button = InlineKeyboardButton(text="Да ✅", callback_data="valid_index")
other_index_button = InlineKeyboardButton(text="Нет ❌", callback_data="other_index")
keyboard_index_confirmation = InlineKeyboardMarkup(inline_keyboard=[[valid_index_button],
                                                                   [other_index_button]])


back_to_index_button = InlineKeyboardButton(text = "Назад ⬅️", callback_data="back_to_index")
keyboard_back_to_index = InlineKeyboardMarkup(inline_keyboard=[[back_to_index_button]])


back_to_order_button = InlineKeyboardButton(text="Назад ⬅️️", callback_data="back_to_order_menu")
keyboard_back_to_order = InlineKeyboardMarkup(inline_keyboard=[[back_to_order_button]])


bot_stats_button = InlineKeyboardButton(text="Статистика 📈", callback_data="statistics_utils")
orders_list_button = InlineKeyboardButton(text="Заказы 📋", callback_data="orders_list")
keyboard_admin_panel = InlineKeyboardMarkup(inline_keyboard=[[orders_list_button],
                                                              [bot_stats_button],
                                                              [back_to_start_button]])