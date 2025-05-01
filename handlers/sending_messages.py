from create_bot import bot
from data_base import sqlite_db


async def sending_schedule(name):
    users = await sqlite_db.get_only_such_users(name)
    group = await sqlite_db.get_group(name)
    for user in users:
        await bot.send_photo(user[0], group[0][1], caption='РАСПИСАНИЕ ВАШЕЙ ГРУППЫ ОБНОВЛЕНО')
