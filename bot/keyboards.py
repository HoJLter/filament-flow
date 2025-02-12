from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import admin_ids
from aiogram.fsm.context import FSMContext

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


back_to_settings_button = InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_settings")
back_to_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_settings_button]])


back_to_admin_button = InlineKeyboardButton(text="Назад ⬅️️", callback_data="back_admin_panel")
back_to_admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_to_admin_button]])


back_to_index_button = InlineKeyboardButton(text = "Назад ⬅️", callback_data="back_to_index")
keyboard_back_to_index = InlineKeyboardMarkup(inline_keyboard=[[back_to_index_button]])


back_to_order_button = InlineKeyboardButton(text="Назад ⬅️️", callback_data="back_to_order_menu")
keyboard_back_to_order = InlineKeyboardMarkup(inline_keyboard=[[back_to_order_button]])


bot_stats_button = InlineKeyboardButton(text="Статистика 📈", callback_data="statistics_utils")
orders_list_button = InlineKeyboardButton(text="Заказы 📋", callback_data="orders_list")
keyboard_admin_panel = InlineKeyboardMarkup(inline_keyboard=[[orders_list_button],
                                                              [bot_stats_button],
                                                              [back_to_start_button]])


async def create_order_keyboard(i):
    confirm_button = InlineKeyboardButton(text=f"Ответить на заказ №{i} ✅", callback_data=f"confirm_order_{i}")
    decline_button = InlineKeyboardButton(text=f"Отклонить заказ №{i} ❌", callback_data=f"decline_order_{i}")
    confirm_order_keyboard = InlineKeyboardMarkup(inline_keyboard=[[confirm_button],
                                                                   [decline_button]])
    return confirm_order_keyboard


async def gen_settings_keyboard(state: FSMContext):
    settings = (await state.get_data())['orders_settings_dict']

    nozzle_temperature_button = InlineKeyboardButton(text="🌡 Температура сопла", callback_data="nozzle_temperature")
    table_temperature_button = InlineKeyboardButton(text="🌡 Температура стола", callback_data="table_temperature")
    printing_speed_button = InlineKeyboardButton(text="🪽 Скорость печати", callback_data="printing_speed")
    layer_thickness_button = InlineKeyboardButton(text="🔪 Толщина слоя", callback_data="layer_thickness")
    send_to_print_button = InlineKeyboardButton(text="🔖 Отправить на печать", callback_data='send_to_print')
    back_to_admin_order = InlineKeyboardButton(text="Назад ⬅️", callback_data=f'back_to_adm_orders')

    keyboard = [[nozzle_temperature_button],
                [table_temperature_button],
                [printing_speed_button],
                [layer_thickness_button],
                [back_to_admin_order]]

    if all(setting for setting in settings.values()):
        keyboard = [[nozzle_temperature_button],
                    [table_temperature_button],
                    [printing_speed_button],
                    [layer_thickness_button],
                    [send_to_print_button],
                    [back_to_admin_order]]

    printing_settings_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return printing_settings_keyboard



model_search_button = InlineKeyboardButton(text="Поиск 🔎", callback_data="model_search")
keyboard_models_lib_menu = InlineKeyboardMarkup(inline_keyboard=[[model_search_button],
                                                                 [back_to_start_button]])


back_to_lib_menu_button = InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_lib_menu")
keyboard_back_to_lib_menu = InlineKeyboardMarkup(inline_keyboard=[[back_to_lib_menu_button]])




async def keyboard_choose_model(model_id):
    choose_model_button = InlineKeyboardButton(text = f"Выбрать модель №{model_id}", callback_data=f"choose_model{model_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[choose_model_button]])
    return keyboard


async def keyboard_page_change(page_number, state: FSMContext):
    pages = (await state.get_data())['pages']
    back_page_button = InlineKeyboardButton(text= "Назад ⬅️", callback_data=f"page_{max(page_number-1, 0)}")
    next_page_button = InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"page_{min(page_number + 1, len(pages))}")
    back_to_order_menu_button = InlineKeyboardButton(text="⬇️ Обратно в меню ⬇️", callback_data="back_to_lib")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_page_button, next_page_button],
                                                     [back_to_order_menu_button]])
    return keyboard