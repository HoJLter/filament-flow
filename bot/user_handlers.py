#Телеграм API
import re
from datetime import datetime

import aiohttp
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, User, URLInputFile
#Асинхронность
import asyncio
#База данных
import asyncpg

from bot.features import get_coordinates, get_static_map, virus_scan
#Импорты из проекта
from bot.fsm import StatesData
from bot.texts import *
from bot.keyboards import keyboard_start_gen, keyboard_back_to_start, keyboard_order_menu, keyboard_admin_panel, \
    keyboard_back_to_order, keyboard_index_confirmation, keyboard_back_to_index, keyboard_file_send
from config import database_config
from database_management.database_filling import fill_clients_info
from config import TOKEN


user_router = Router()


@user_router.message(Command("start", prefix="/"))
async def welcome_command(message: Message, state: FSMContext):
    await state.set_state(StatesData.none_state)
    await message.delete()
    user = message.from_user
    user_data = {
        'user_id':user.id,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'username':user.username
    }
    await fill_clients_info(**user_data)
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
async def main_menus(callback:CallbackQuery, state: FSMContext):
    if callback.data == "create_order":
        order_parameters = {
            'order_name': None,
            'reference': None,
            'mail_index': None,
            'file_id': None,
            'file_uid': None,
            'file_name': None,
        }
        await state.update_data(order_parameters=order_parameters)
        await callback.message.edit_media(media=InputMediaPhoto(media=image_order_menu,
                                                                caption=await text_order_menu_gen(state)),
                                          reply_markup=keyboard_order_menu)

    elif callback.data ==  'back_to_order_menu':
        await state.set_state(StatesData.none_state)
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
async def set_order_parameters(callback: CallbackQuery, state: FSMContext):
    if callback.data == "order_name":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_order_name, caption="Укажите наименование заказа:"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_order_name)

    elif callback.data == "reference":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_reference, caption="Укажите техническое задание:"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_references)

    elif callback.data == "mail_index":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_mail_indexes, caption="Укажите почтовый индекс Почты России:"),
                                          reply_markup=keyboard_back_to_order)
        await state.set_state(StatesData.waiting_for_index)

    elif callback.data == "send_file":
        await callback.message.edit_media(media=InputMediaPhoto(media=image_file, caption="Отправьте .stl модель для печати"),
                                          reply_markup=keyboard_file_send)
        await state.set_state(StatesData.waiting_for_file)

    elif callback.data == "complete_button":
        order_parameters = (await state.get_data())['order_parameters']
        print(order_parameters)
        if (order_parameters['order_name'] and order_parameters['reference'] and order_parameters['mail_index'] and
                (order_parameters['file_id'] or order_parameters['file_uid'])):
            connection = await asyncpg.connect(**database_config)
            now = datetime.now()
            user = (await state.get_data())['user']

            reg_date = datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
            await connection.execute(f'UPDATE filflow_scheme.clients SET order_count = order_count + 1 WHERE id_client= {user.id}')

            order_id = await connection.fetchval("INSERT INTO filflow_scheme.orders (id_client, reg_date, status)"
                                                 f"VALUES ('{user.id}', '{reg_date}', 'НА РАССМОТРЕНИИ') RETURNING id_order")
            print(len(order_parameters['file_id']))
            await connection.execute("INSERT INTO fiflow_scheme.order_info(id_order, reference, id_mail, order_name, id_tg_file) "
                                     f"VALUES ({order_id}, '{order_parameters['reference']}', {order_parameters['mail_index']}, "
                                     f"'{order_parameters['order_name']}', '{order_parameters['file_id']}')")

            await connection.close()
            await state.update_data(order_name=None, mail_index=None, advices=None)
            temporal_message = await callback.message.answer(text_order_edit_complete)
            await state.set_state(StatesData.none_state)

            order_parameters = {
                'order_name': None,
                'reference': None,
                'mail_index': None,
                'file_id': None,
                'file_uid': None,
                'file_name': None,
            }

            await state.update_data(order_parameters=order_parameters)
            await callback.message.edit_media(media=InputMediaPhoto(media=image_order_menu,
                                                                    caption=await text_order_menu_gen(state)),
                                              reply_markup=keyboard_order_menu)

            await asyncio.sleep(3)
            await temporal_message.delete()
        else:
            temporal_message = await callback.message.answer(text=text_order_edit_failed)
            await asyncio.sleep(3)
            await temporal_message.delete()


@user_router.callback_query(lambda callback: callback.data == "valid_index")
async def valid_index(callback: CallbackQuery, state: FSMContext):

    await back_to_order_config(state)


@user_router.message(StateFilter(StatesData.waiting_for_references,
                                 StatesData.waiting_for_order_name))
async def set_simple_params(message: Message, state:FSMContext):
    current_state = await state.get_state()
    order_parameters = (await state.get_data())['order_parameters']

    if current_state == StatesData.waiting_for_order_name:
        await message.delete()
        order_parameters['order_name'] = message.text
        await back_to_order_config(state)

    elif current_state == StatesData.waiting_for_references:
        await message.delete()
        order_parameters['reference'] = message.text
        await back_to_order_config(state)


async def back_to_order_config(state: FSMContext):
    message = (await state.get_data())['master_msg']
    await state.set_state(StatesData.none_state)
    try:
        await message.edit_media(media=InputMediaPhoto(media=image_order_menu,
                                                                caption=await text_order_menu_gen(state)),
                                          reply_markup=keyboard_order_menu)
    except:
        pass


@user_router.message(StatesData.waiting_for_file)
async def set_file(message: Message, state: FSMContext):
    await message.delete()
    try:
        if (message.content_type == ContentType.DOCUMENT and
            message.document.file_name.lower().endswith(".stl")):
            order_parameters = (await state.get_data())['order_parameters']
            try:
                file_info_url = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={message.document.file_id}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_info_url) as file_info:
                        response_json = await file_info.json()
                        if response_json['ok']:
                            file_path = response_json['result']['file_path']
                            download_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
                            async with session.get(download_url) as response:
                                file_bytes = response.content
                                temp_msg = await message.answer(text="Подождите 10 секунд.. Файл проверяется на вирусы.")
                                is_virus=await virus_scan(file_bytes)
                                await temp_msg.delete()
                                if is_virus == False:
                                    order_parameters['file_name'] = message.document.file_name
                                    order_parameters['file_id'] = message.document.file_id
                                    await back_to_order_config(state)
                                    await state.set_state(StatesData.none_state)
            except Exception as e:
                print(e)
            order_parameters['file_name'] = message.document.file_name
            order_parameters['file_id'] = message.document.file_id
            await back_to_order_config(state)
            await state.set_state(StatesData.none_state)
        else:
            temporary_message = await message.answer(text=f"Ошибка ‼️ Вы отправили файл разрешения "
                                                          f".{message.document.file_name.lower().split('.')[-1]}, "
                                                          f"а нужен .stl")
            await asyncio.sleep(6)
            await temporary_message.delete()
            await state.set_state(StatesData.waiting_for_file)
    except Exception as e:
        print(e)
        temporary_message = await message.answer(text="Неизвестная ошибка ‼️ Попробуйте еще раз")
        try:
            await message.delete()
        except:
            pass
        await asyncio.sleep(4)
        await temporary_message.delete()
        await state.set_state(StatesData.waiting_for_file)


@user_router.callback_query(lambda callback: callback.data == "back_to_index")
@user_router.callback_query(lambda callback: callback.data == 'mail_index')
async def mail_indexes(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_media(media=InputMediaPhoto(media=image_mail_indexes, caption="Отправьте индекс отделения Почты России:"),
                                      reply_markup=keyboard_back_to_order)
    await state.set_state(StatesData.waiting_for_index)


@user_router.message(StatesData.waiting_for_index)
async def set_index(message: Message, state: FSMContext):
    connection = await asyncpg.connect(database=database_config['database'], user=database_config['user'],
                               password=database_config['password'], host=database_config['host'])
    formatted_index = re.sub(r'\D','' ,(message.text.replace(" ", "")))
    response = await connection.fetchrow("SELECT id_mail,region, autonom, area, city, city_1 "
                                        "FROM filflow_scheme.mail_indexes "
                                       f"WHERE id_mail={formatted_index or 000000}")
    data = await state.get_data()
    main_message = data['master_msg']
    await state.update_data(mail_index=message.text)
    if response:
        region = str(response['region']) if 'region' in response else ""
        autonom = str(response['autonom']) if 'autonom' in response else ""
        area = str(response['area']) if 'area' in response else ""
        city = str(response['city']) if 'city' in response else ""
        city_1 = str(response['city_1']) if 'city_1' in response else ""

        location = (f"{region.capitalize()+',' if region else ""} "
                    f"{autonom.capitalize()+',' if autonom else ""} "
                    f"{area.capitalize()+',' if area else ""} "
                    f"{city.title()} "
                    f"{city_1.title()}")

        formatted_location = " ".join(location.split())
        await message.delete()
        order_parameters = (await state.get_data())['order_parameters']
        order_parameters['mail_index'] = response['id_mail']
        await state.update_data(order_parameters=order_parameters)
        try:
            cords = await get_coordinates(formatted_index)
            maps = await get_static_map(cords)
            await main_message.edit_media(media=InputMediaPhoto(media=maps,
                                                caption = f"Вы указали индекс {response['id_mail']}. "
                                                f"Он соответствует региону {formatted_location}."
                                                f"\nЭто верно?"), reply_markup=keyboard_index_confirmation)
        except Exception as e:
            await main_message.edit_caption(caption = f"Вы указали индекс {response['id_mail']}. "
                                                f"Он соответствует региону {formatted_location}."
                                                f"\nЭто верно?", reply_markup=keyboard_index_confirmation)

    else:
        await message.delete()
        await state.update_data(mail_index=None)
        await main_message.edit_caption(caption = text_index_error, reply_markup=keyboard_back_to_index)


@user_router.callback_query(lambda callback: callback.data == "other_index")
@user_router.callback_query(lambda callback: callback.data == "index_error")
async def index_error(callback: CallbackQuery, state: FSMContext):
    await state.update_data(mail_index=None)
    await mail_indexes(callback, state)


@user_router.message(F.photo)
async def photo_test(message: Message):
    print(message.photo[-1])


@user_router.message(StatesData.none_state)
async def delete_useless(message:Message):
    await message.delete()