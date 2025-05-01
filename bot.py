''''
╔══╦═══╦╗╔╦══╗╔═══╦════╗
║╔╗║╔═╗║║║║╔╗║║╔══╩═╗╔═╝
║║║║╚═╝║║║║╚╝╚╣╚══╗─║║
║║║║╔══╣║╔║╔═╗║╔══╝─║║
║║║║║──║╚╝║╚═╝║╚══╗─║║
╚╝╚╩╝──╚══╩═══╩═══╝─╚╝
'''



from aiogram import Dispatcher # type: ignore
import asyncio

from create_bot import bot, dp
from handlers import admin_router, router
from data_base import sqlite_db



async def on_startup():
        await sqlite_db.sql_start()
        dp.include_router(admin_router)
        dp.include_router(router)
    

async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())



"""
░░░░░░░░░░░░▄▐░░░░░░░░░░
░░░░░░▄▄▄░░▄██▄░░░░░░░░░
░░░░░▐▀█▀▌░░░░▀█▄░░░░░░░
░░░░░▐█▄█▌░░░░░░▀█▄░░░░░░
░░░░░░▀▄▀░░░▄▄▄▄▄▀▀░░░░░░
░░░░▄▄▄██▀▀▀▀░░░░░░░░░░░░
░░░█▀▄▄▄█░▀▀░░░░░░░░░░░░
░░░▌░▄▄▄▐▌▀▀▀░░░░░░░░░░░
▄░▐░░░▄▄░█░▀▀░░░░░░░░░░░
▀█▌░░░▄░▀█▀░▀░░░░░░░░░░░░
░░░░░░░▄▄▐▌▄▄░░░░░░░░░░░░
░░░░░░░▀███▀█░▄░░░░░░░░░
░░░░░░▐▌▀▄▀▄▀▐▄░░░░░░░░░
░░░░░░▐▀░░░░░░▐▌░░░░░░░░░
░░░░░░█░░░░░░░░█░░░░░░░░░
░░░░░▐▌░░░░░░░░░█░░░░░░
░░░░░█░░░░░░░░░░▐▌░░░░░░
"""