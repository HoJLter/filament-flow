import json

import aiofiles
import aiogram
import asyncio
import aiohttp
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile, URLInputFile
from bot.texts import *
from bot.keyboards import *
from bot.fsm import *
from aiogram import exceptions

features_router = Router()


@features_router.callback_query(lambda callback: callback.data == "lib_menu")
async def show_lib_menu(callback: CallbackQuery, state: FSMContext):
    """Открывает меню для работы с библиотекой моделей"""
    await state.set_state(StatesData.none_state)
    await callback.message.edit_media(media=InputMediaPhoto(media=image_models_lib_menu, caption=text_models_lib),
                                        reply_markup=keyboard_models_lib_menu)


@features_router.callback_query(lambda callback: callback.data == "model_search")
async def search_request(callback: CallbackQuery, state: FSMContext):
    """Просьба ввести поисковой запрос"""
    temp_search_request = await callback.message.edit_caption(caption="Введите поисковой запрос (на английском):", reply_markup=keyboard_back_to_lib_menu)
    await state.update_data(temp_search_request=temp_search_request)
    await state.set_state(StatesData.waiting_for_search)


@features_router.message(StatesData.waiting_for_search)
async def search_processing(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
    await (await state.get_data())['temp_search_request'].delete()
    await message.delete()
    await state.set_state(StatesData.none_state)
    search_expression = message.text
    params = {
        "downloadable": "True",
        "file_format": "stl",
        "sort_by":"likeCount",
        "q": f"{search_expression}"
    }

    url = "https://sketchfab.com/v3/search?type=models"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            results = (await response.json())['results']
        # Список для хранения изображений и данных о моделях
        models_info = []

        for model_id, res in enumerate(results, start=1):
            name = res['name']
            publish_date = res['publishedAt']
            user = res['user']
            model_uid = res['uid']
            viewer_url = res['viewerUrl']

            imgs_sizes = [[photo['size'], photo['url']] for photo in res['thumbnails']['images']]
            selected_image_url = sorted(imgs_sizes, reverse=True)[min(len(imgs_sizes) // 2 - 1, 0)][1]

            models_info.append({
                'photo': selected_image_url,
                'caption': f"Имя: {name} \n"
                           f"Дата публикации: {publish_date}\n"
                           f"Автор: {user['profileUrl']}\n"
                           f"UID модели: {model_uid}\n"
                           f"<a href='{viewer_url}'>Предпросмотр модели</a>",
                'reply_markup': await keyboard_choose_model(model_id, model_uid, name),
                'parse_mode':'HTML'
            })

        pages = [models_info[i:i + 5] for i in range(0, len(models_info), 5)]
        await state.update_data(pages=pages)

        temp_page = []
        try:
            for model in pages[0]:
                temp_page.append(await message.answer_photo(**model))

            last_page_msg = await message.answer(text ="*|---------------------|Это конец страницы №1|---------------------|*",
                                 reply_markup=await keyboard_page_change(0, state),
                                 parse_mode="Markdown")
            await state.update_data(temp_page=temp_page)
            await state.update_data(last_page_msg=last_page_msg)
        except IndexError:
            temp_search_request = await message.answer(text="Ошибка ‼️. Моделей не найдено. \n"
                                                            "Введите поисковой запрос (на английском):",
                                                       reply_markup=keyboard_back_to_lib_menu)
            await state.update_data(temp_search_request=temp_search_request)
            await state.set_state(StatesData.waiting_for_search)



@features_router.callback_query(lambda callback: callback.data.startswith("page"))
async def page_switch(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    temp_page = data['temp_page']
    pages = data['pages']

    page_number = min(int(callback.data.split("_")[-1]), len(pages)-1)

    for message in temp_page:
        await message.delete()

    temp_page = []
    await callback.message.delete()
    for model in pages[page_number]:
        temp_page.append(await callback.message.answer_photo(**model))
    await state.update_data(temp_page=temp_page)

    last_page_msg = await callback.message.answer(text=f"*|---------------------|Это конец страницы №{page_number+1}|---------------------|*",
                                  reply_markup=await keyboard_page_change(page_number, state),
                                  parse_mode="Markdown")
    await state.update_data(last_page_msg=last_page_msg)
    await state.update_data(master_msg=last_page_msg)


@features_router.callback_query(lambda callback: callback.data == "back_to_lib")
async def back_to_lib_menu(callback:CallbackQuery, state: FSMContext):
    try:
        temp_page = (await state.get_data())['temp_page']
        for msg in temp_page:
            await msg.delete()
    except:
        pass
    await callback.message.delete()
    master_msg = await callback.message.answer_photo(photo=image_models_lib_menu, caption=text_models_lib,
                               reply_markup=keyboard_models_lib_menu)
    await state.update_data(master_msg=master_msg)



@features_router.callback_query(lambda callback: len(callback.data)==32)
async def choose_model(callback: CallbackQuery, state: FSMContext):
    order_parameters = (await state.get_data())['order_parameters']
    order_parameters['file_uid'] = callback.data
    order_parameters['file_name'] = callback.data
    try:
        temp_page = (await state.get_data())['temp_page']
        for msg in temp_page:
            await msg.delete()
        await (await state.get_data())['last_page_msg'].delete()
    except:
        pass

    await state.set_state(StatesData.none_state)
    master_msg = await callback.message.answer_photo(photo=image_order_menu,
                                      caption=await text_order_menu_gen(state),
                                      reply_markup=keyboard_order_menu)
    await state.update_data(master_msg=master_msg)


# -----------------------------------------------------------------------------------------------
# КАРТЫ
import aiohttp
from io import BytesIO
from PIL import Image

async def get_coordinates(search_request):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'user_agent': "FilamentFlow",
        'q': f"{search_request}",
        'format': 'json',
        'limit': 1,
        'countrycodes': ['ru'],
        'type':'postcode'

    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            print(json.dumps(await response.json(), indent=4, ensure_ascii=False))
            lat = (await response.json())[0]['lat']
            lon = (await response.json())[0]['lon']
    return [lat, lon]



async def get_static_map(cords):
    static_apikey = 'e28bffb5-07a8-456a-9a94-fab9adf615ee'
    image = URLInputFile(
        f"https://static-maps.yandex.ru/v1?apikey={static_apikey}&ll={cords[1]},{cords[0]}&lang=ru_RU&size=450,250&spn=0.03,0.03",
        filename="map.png")
    return image

# -----------------------------------------------------------------------------------------------
# СКАНИРОВАНИЕ НА ВИРУСЫ
async def virus_scan(file):
    """Сканирование на вирусы с помощью API virustotal"""
    send_file_url = 'https://www.virustotal.com/api/v3/files'

    header = {
        'x-apikey': '759aa67d69e969ef6778115aa207c7b1590cbc3564bf409a6dae1e31322c7790'
    }

    data = aiohttp.FormData()
    data.add_field("file", file, filename="test", content_type='application/octet-stream')

    async with aiohttp.ClientSession() as session:
        async with session.post(send_file_url, headers=header, data=data) as response:
            analise_id = (await response.json())['data']['id']
            analise_url = f'https://www.virustotal.com/api/v3/analyses/{analise_id}'

            await asyncio.sleep(10)

            async with session.get(analise_url, headers=header) as response:
                stats =  (await response.json())['data']['attributes']['stats']
                if stats['undetected']>30:
                    return False
                else:
                    return True