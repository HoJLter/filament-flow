import json

import aiogram
import asyncio
import aiohttp
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputFile
from bot.texts import *
from bot.keyboards import *
from bot.fsm import *
from aiogram import exceptions

features_router = Router()


@features_router.message(Command("start", prefix="/"))
async def show_lib_menu(message: Message, state: FSMContext):
    """Открывает меню для работы с библиотекой моделей"""
    await message.delete()
    await message.answer_photo(photo=image_models_lib_menu, caption=text_models_lib,
                               reply_markup=keyboard_models_lib_menu)


@features_router.callback_query(lambda callback: callback.data == "model_search")
async def search_request(callback: CallbackQuery, state: FSMContext):
    """Просьба ввести поисковой запрос"""
    await callback.message.edit_caption(caption="Введите поисковой запрос (на английском):", reply_markup=keyboard_back_to_lib_menu)
    await state.set_state(StatesData.waiting_for_search)


@features_router.message(StatesData.waiting_for_search)
async def search_processing(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
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
                'reply_markup': await keyboard_choose_model(model_id),
                'parse_mode':'HTML'
            })

        pages = [models_info[i:i + 5] for i in range(0, len(models_info), 5)]
        await state.update_data(pages=pages)

        temp_page = []
        for model in pages[0]:
            temp_page.append(await message.answer_photo(**model))

        await message.answer(text ="*|---------------------|Это конец страницы №1|---------------------|*",
                             reply_markup=await keyboard_page_change(0, state),
                             parse_mode="Markdown")
        await state.update_data(temp_page=temp_page)



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

    await callback.message.answer(text=f"*|---------------------|Это конец страницы №{page_number+1}|---------------------|*",
                                  reply_markup=await keyboard_page_change(page_number, state),
                                  parse_mode="Markdown")


@features_router.callback_query(lambda callback: callback.data == "back_to_lib")
async def back_to_lib_menu(callback:CallbackQuery, state: FSMContext):
    temp_page = (await state.get_data())['temp_page']
    for msg in temp_page:
        await msg.delete()
    await callback.message.delete()
    await callback.message.answer_photo(photo=image_models_lib_menu, caption=text_models_lib,
                               reply_markup=keyboard_models_lib_menu)
