import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN
from bot.features import features_router

async def main():
    tasks = [run_bot()]
    await asyncio.gather(*tasks)


async def run_bot():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(features_router)
    print("[INFO] SESSION HAS BEEN OPENED")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        print("[INFO] SESSION HAS BEEN CLOSED")


