"""
__________$$$$$$$$$$$$$$$$$$$$$$
_________oo$$$$$$$$$$$$$$$$$$$$$$$$
________$$$$___$$$$$$$$$$$$$$$$$$$$$
______$$$$______$$$$$$$$$$$$$$$$$$$$$$
____$$$$$________$$$$$$$$$$$$$$$$$$$$$$$
___$$$$$__________$$$$$$$$$$$$$$$$$$$$$$$
__$$$$$____________$$$$$$$$$$$$$$$$$$$$$$$
_$$$$$$____________$$$$$$$$$$$$$$$$$$$$$$$$
_$$$$$$___________$$$$$$$$$___________$$$$$$
_$$$$$$$_________$$$_$$$_$$$_________$$$$$$$
_$$$$$$$$______$$$$___$___$$$$______$$$$$$$$
_$$$$$$$$$$$$$$$$$___$$$___$$$$$$$$$$$$$$$$$
_$$$_$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$_o$$
_$$$__$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$__$$$
__$$$__$'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$__o$$$
__'$$o__$$__$$'$$$$$$$$$$$$$$'$$__$$_____o$$
____$$o$____$$__'$$'$$'$$'__$$______$___o$$
_____$$$o$__$____$$___$$___$$_____$$__o$
______'$$$$O$____$$____$$___$$ ____o$$$
_________'$$o$$___$$___$$___$$___o$$$
___________'$$$$o$o$o$o$o$o$o$o$$$$ 

"""

import sqlite3
from pathlib import Path


token_bot = '7763825766:AAHJHy7B1WezT86zd-d70nSYAUQSsJbtee8'

# Инициализация базы администраторов
ADMINS_DB = Path('config.db')

def init_admins_db():
    #Инициализирует базу администраторов"""
    with sqlite3.connect(ADMINS_DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS admins (
                      username TEXT PRIMARY KEY,
                      added_by TEXT)''')  # Храним только username
        # Добавляем первого админа если база пуста
        if not conn.execute('SELECT 1 FROM admins').fetchone():
            conn.execute('INSERT INTO admins VALUES (?, ?)', ("usermane04", "system"))

def add_admin_sync(username: str, added_by: str):
    #Добавляет администратора по username"""
    with sqlite3.connect(ADMINS_DB) as conn:
        conn.execute('INSERT OR IGNORE INTO admins VALUES (?, ?)', (username.lower(), added_by.lower()))

def get_admins_sync():
    #Возвращает список username администраторов"""
    with sqlite3.connect(ADMINS_DB) as conn:
        return [row[0] for row in conn.execute('SELECT username FROM admins')]

def is_admin_sync(username: str) -> bool:
    #Проверяет, является ли пользователь администратором"""
    with sqlite3.connect(ADMINS_DB) as conn:
        return conn.execute('SELECT 1 FROM admins WHERE username = ?', (username.lower(),)).fetchone() is not None
    
def remove_admin_sync(username: str):
    #Удаляет администратора по username"""
    with sqlite3.connect(ADMINS_DB) as conn:
        conn.execute('DELETE FROM admins WHERE username = ?', (username.lower(),))

def count_admins_sync() -> int:
    #Возвращает количество администраторов"""
    with sqlite3.connect(ADMINS_DB) as conn:
        return conn.execute('SELECT COUNT(*) FROM admins').fetchone()[0]


# Инициализируем базу при импорте
init_admins_db()