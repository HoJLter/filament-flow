import asyncio
from aiogram import Bot, Dispatcher

from bot.admin_handlers import admin_router
from config import TOKEN
from bot.user_handlers import user_router
from database_management.database_filling import check_updates


async def main():
    tasks = [run_bot(), check_updates()]
    await asyncio.gather(*tasks)


async def run_bot():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("[INFO] SESSION HAS BEEN OPENED")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        print("[INFO] SESSION HAS BEEN CLOSED")


