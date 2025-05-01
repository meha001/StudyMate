import sqlite3
from datetime import datetime
from sqlite3 import IntegrityError
from create_bot import bot

base = sqlite3.connect('sharaga.db')
cursor = base.cursor()


async def sql_start():
    if base:
        print('База данных подключена!')
    cursor.execute('CREATE TABLE IF NOT EXISTS users (tg_id INTEGER, name_group TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS news (dt DATETIME, title TEXT, content TEXT, img TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS groups (name TEXT PRIMARY KEY, schedule TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS questions (user_id INT, question TEXT, nick TEXT)')
    base.commit()


async def delete_question(question_id: int):
    """Удаляет конкретный вопрос по его ID"""
    cursor.execute('DELETE FROM questions WHERE rowid = ?', (question_id,))
    base.commit()

async def get_all_questions():
    """Возвращает вопросы с их ID"""
    return cursor.execute('SELECT rowid, * FROM questions').fetchall()

async def get_all_questions():
    cursor.execute('SELECT rowid, * FROM questions')
    return cursor.fetchall()

async def add_question(data: dict):  # ← Принимаем готовый словарь
    cursor.execute('INSERT INTO questions VALUES (?, ?, ?, ?)', 
                  (data['user_id'], data['question'], data['nick'], 0))
    base.commit()

async def get_unanswered_questions_with_groups():
    """Получаем вопросы с информацией о группе"""
    cursor.execute('''
        SELECT q.rowid, q.user_id, q.question, q.nick, u.name_group 
        FROM questions q
        JOIN users u ON q.user_id = u.tg_id
        WHERE q.answered = 0
    ''')
    return cursor.fetchall()


async def get_group(name):
    return [i for i in cursor.execute('SELECT * FROM groups WHERE name = ?', (name,))]


async def get_only_such_users(name):
    return [i for i in cursor.execute('SELECT * FROM users WHERE name_group = ?', (name,))]


async def create_schedule(data: dict):  # Принимаем обычный словарь
    try:
        cursor.execute(
            'UPDATE groups SET schedule = ? WHERE name = ?',
            (data['image'], data['group'])
        )
        base.commit()
    except Exception as e:
        print(f"Ошибка при обновлении расписания: {e}")
        raise


async def delete_schedule(name):
    cursor.execute('UPDATE groups SET schedule = ? WHERE name = ?', (None, name))
    base.commit()


async def add_user(user_id):
    cursor.execute('INSERT INTO users VALUES (?, ?)', (user_id, 'no_group'))
    base.commit()
    
async def get_news_by_id(news_id: int):
    """Получает новость по ID"""
    cursor.execute('SELECT rowid, * FROM news WHERE rowid = ?', (news_id,))
    return cursor.fetchone()

async def get_data_from_proxy(state_or_data):
    """Универсальная функция для получения данных"""
    if hasattr(state_or_data, 'get_data'):  # Если это FSMContext
        return await state_or_data.get_data()
    return state_or_data  # Если уже словарь 


async def add_news(state):
    proxy_data = await get_data_from_proxy(state)
    cursor.execute('INSERT INTO news VALUES (?, ?, ?, ?)', (datetime.now(),) + tuple(proxy_data.values()))
    base.commit()


async def get_news():
    return [n for n in cursor.execute('SELECT * FROM news')]


async def delete_news(date_str: str):
    """Удаляет новость по дате"""
    try:
        cursor.execute('DELETE FROM news WHERE dt = ?', (date_str,))
        base.commit()
    except Exception as e:
        print(f"Ошибка при удалении новости: {e}")
        raise

async def get_all_groups():
    """Получить все группы"""
    cursor.execute("SELECT name FROM groups")
    return cursor.fetchall()
    
async def delete_group(group_name: str):
    """Удалить группу"""
    cursor.execute("DELETE FROM groups WHERE name = ?", (group_name,))
    base.commit()


async def add_group(name, msg):
    try:
        cursor.execute('INSERT INTO groups VALUES (?, ?)', (name, None))
        base.commit()
    except IntegrityError:
        bot.send_message(msg.chat.id, 'Данная группа уже создана!')


async def get_all_users():
    return [u for u in cursor.execute('SELECT * FROM users')]


async def change_user_group(user_id, group_name):
    cursor.execute('UPDATE users SET name_group = ? WHERE tg_id = ?', (group_name, user_id))
    base.commit()


async def get_user_group(user_id: int) -> str:
    """Получаем группу пользователя"""
    cursor.execute('SELECT name_group FROM users WHERE tg_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

async def mark_question_as_answered(question_id: int):
    """Пометить вопрос как отвеченный с проверкой"""
    try:
        cursor.execute(
            'UPDATE questions SET answered = 1 WHERE rowid = ?',
            (question_id,)
        )
        base.commit()
        return True
    except Exception as e:
        
        return False

async def get_answered_questions():
    """Получить отвеченные вопросы"""
    cursor.execute('SELECT rowid, * FROM questions WHERE answered = 1')
    return cursor.fetchall()