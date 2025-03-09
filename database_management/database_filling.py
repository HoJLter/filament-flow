import aiohttp
import asyncio
import asyncpg
from hashlib import sha256
import aiofiles
from aiohttp import ClientSession
from dbfread import DBF
from lxml import html
from zipfile import ZipFile
import requests
from config import database_config


async def get_file_url() -> str:
    """Получаю URL файла из HTML страницы"""
    url = "https://www.pochta.ru/support/database/ops"
    async with ClientSession() as session:
        async with session.get(url=url) as response:
            tree = html.fromstring(await response.text())
            path = '/html/body/div[1]/div[3]/div/div/div/div/div/div/div/div[1]/article/div/div/p[3]/a'
            link = tree.xpath(path)
            file_url = link[0].get("href")
            file_url=f"https://www.pochta.ru{file_url}"
        return file_url


async def unpack_zip(path):
    """Распаковываю zip-архив"""
    with ZipFile(path, 'r') as file:
        file.extractall("data/")
        return file.namelist()


async def download_dbf():
    """Скачиваю файл, используя ссылку, полученную от функции get_file_url"""
    url = await get_file_url()
    response = requests.get(url).content
    path = "data/mail_idx.zip"
    with open(path,"wb") as file:
        file.write(response)
    dbf_name = await unpack_zip(path)
    return dbf_name


async def insert_task(connection, value):
    """Создание задачи"""
    await connection.execute(f"INSERT INTO filflow_scheme.mail_indexes(id_mail, region, autonom, area, city, city_1)"
                               f"VALUES {value}")


async def create_insert_array(dbf):
    all_idx = [[record["INDEX"],record["REGION"], record["AUTONOM"], record["AREA"], record["CITY"], record["CITY_1"]] for record in dbf]
    batched_idx = [all_idx[i:i+1000] for i in range(0, len(all_idx), 1000)]
    res = []
    for idx_ar in batched_idx:
        temp_values = ""
        for idx in idx_ar:
            temp_values+=(f"({idx[0]}, '{idx[1]}', '{idx[2]}', "
                          f"'{idx[3]}','{idx[4]}','{idx[5]}'),")
        res.append(temp_values[0:-1])
    return res


async def fill_index_database():
    """Создание списка задач вставки данных в бд"""
    await truncate_mail_indexes()
    dbf_name = await download_dbf()
    pool = await asyncpg.create_pool(user=database_config['user'], password=database_config['password'],
                               database=database_config['database'], host=database_config['host'])
    dbf = DBF(f"data/{"".join(dbf_name)}")
    values_to_insert = await create_insert_array(dbf)
    tasks = [insert_task(connection=pool, value=value) for value in values_to_insert]
    await asyncio.gather(*tasks)
    await pool.close()


async def check_updates():
    """Проверяю сайт с индексами на наличие обновлений раз в 12 часов"""
    while True:
        url = "https://www.pochta.ru/support/database/ops"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url,) as response:
                page_html = html.fromstring(await response.text())
                x_path = '//*[@id="main-content"]/div/div/div/div/div/div/div/div[1]/article/div/div/p[3]/text()'
                paragraph = "".join(page_html.xpath(x_path))
                hash_object = sha256()
                bytecode = paragraph.encode('utf-8')
                hash_object.update(bytecode)
                new_hash = hash_object.hexdigest()
                # Хеширую параграф.
                async with aiofiles.open('data/page_hash.txt', 'r+') as file:
                    old_hash = await file.read()
                    await file.seek(0)
                    await file.write(new_hash)
                if old_hash != new_hash:
                    await fill_index_database()
                    print("[INFO] New data was inserted")
                else:
                    print("[INFO] No updates")
                await asyncio.sleep(43200)


async def truncate_mail_indexes():
    """Очистка старых данных таблицы индексов"""
    connection = await asyncpg.connect(database=database_config['database'], user=database_config['user'],
                               password=database_config['password'], host=database_config['host'])
    await connection.execute("TRUNCATE mail_indexes CASCADE")
    await connection.close()


async def fill_clients_info(user_id, first_name, last_name, username):
    """Заполнение таблицы с информацией о пользователе"""
    try:
        connection = await asyncpg.connect(**database_config)
        await connection.execute("INSERT INTO clients (id_client, first_name, last_name, username, order_count)"
                                 f"VALUES ({user_id}, '{first_name}', '{last_name}', '{username}', 0)")
    except:
        pass
