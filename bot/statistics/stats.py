import asyncpg
from config import database_config
import asyncio
import aiofiles
import json

async def write_regions_statistics():
    while True:
        connection: asyncpg.Connection = await asyncpg.connect(**database_config)
        response = await connection.fetch("""SELECT region FROM filflow_scheme.order_info
                                               JOIN mail_indexes
                                               ON mail_indexes.index = order_info.id_mail""")
        regions_statistics = {}

        for record in response:
            if record['region'] in regions_statistics:
                regions_statistics[record['region']] += 1
            else:
                regions_statistics[record['region']] = 1

        async with aiofiles.open("bot/statistics/regions.json", mode='w+', encoding="utf-8") as file:
            json_data = json.dumps(regions_statistics, ensure_ascii=False)
            await file.write(json_data)
        await asyncio.sleep(1200)


async def create_top_list():
    async with aiofiles.open("regions.json", mode="r", encoding="utf-8") as file:
        content = await file.read()
        content_dict = json.loads(content)

    top_list = sorted(content_dict)[::-1][0:3]
    top_dict = {region:content_dict[region] for region in top_list}
    text = "ℹ️ Самые активные регионы по количеству заказов:\n" + "\n".join(
        [f"📌 {region} - {ord_count}" for region, ord_count in top_dict.items()])
    print(text)
    return text


if __name__ == '__main__':
    asyncio.run(create_top_list())