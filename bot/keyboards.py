from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import admin_ids

async def gen_start_menu_kb(user_id):
    create_order_button = InlineKeyboardButton(text = "Оформить заказ 🖋", callback_data="create_order")
    info_button = InlineKeyboardButton(text = "Информация 📖", callback_data="info")
    buttons = [[create_order_button],
               [info_button]]

    if user_id in admin_ids:
        admin_panel_button = InlineKeyboardButton(text = "Админ-панель 🔐", callback_data="admin_panel")
        buttons.append([admin_panel_button])


    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

