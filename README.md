# 🎓 StudyMate - Telegram-бот для студентов

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)

Бот для помощи студентам и админам. Позволяет просматривать расписание, читать новости, задавать вопросы, а также управлять контентом и пользователями.

---

## 🌟 Возможности

### 👨‍🎓 Для студентов:
- 📅 Просмотр расписания своей группы
- 📰 Актуальные новости
- ❓ Задание вопросов админам
- 🔔 Уведомления об изменениях

### 👑 Для админов:
- 🛠 Управление группами и расписанием
- 📢 Публикация новостей (с фото и текстом)
- 📬 Ответы на вопросы студентов
- 🔄 Массовая рассылка
- 👤 Добавление админов по `@username`

---

### 🔍 Описание модулей
 - bot.py — точка входа. Подключает все обработчики, запускает polling.
 - create_bot.py — создаёт экземпляры Bot и Dispatcher, загружает конфиг.
 - handlers/admin_side.py — административные команды:
 - /create_group, /delete_group, /groups
 - /create_schedule, /delete_schedule
 - /create_news, /delete_news
 - /view_questions, ответы студентам
 - /add_admin, /remove_admin, /list_admins
 - handlers/user_side.py — команды для студентов:
 - /select_group, /schedule, /news, /ask_question, /id, /delete_me_from_group
 - data_base/sqlite_db.py — работа с базой данных:
 - группы, новости, расписания, вопросы и пользователи

---

### 💾 Работа с базой данных
 - Используется встроенная SQLite-база. Основные таблицы:
 - groups — группы студентов
 - schedules — изображения расписаний, привязанные к группам
 - news — заголовки, тексты и фото новостей
 - questions — вопросы студентов, статус ответа
 - users — Telegram ID студентов и их группы
 - Все операции реализованы через асинхронные функции. Подключение к базе происходит через sqlite_db.py и config.py.

---

### ➕ Расширение проекта
## Чтобы добавить новую команду:
 - Определи хендлер (обработчик) в admin_side.py или user_side.py.
 - Используй @admin_router.message(...) или @user_router.message(...) с фильтрами.
 - Добавь команду в dispatcher.include_router(...) в bot.py, если используешь новый Router.
 - При необходимости — добавь методы в sqlite_db.py и обнови базу.

---

### 👨‍💻 Поддержка и сопровождение
 - Развёртыванием занимается системный администратор.
 - Программисты расширяют функциональность через обработчики и работу с БД.
 - Все сообщения используют ParseMode.HTML для форматирования.
 - Используются ReplyKeyboardMarkup и InlineKeyboardMarkup для удобного взаимодействия.

---

## 🚀 Быстрый старт

### 1. Скачай проект:

```bash
git clone https://github.com/NABIEVMEHRUBON/StudyMate.git
cd StudyMateBot
```

### 2. Настрой окружение:

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 3. Установи зависимости:

```bash
pip install -r aiogram
```

### 4. Пропиши:

```bash
TOKEN_BOT="ваш_токен_бота"
ADMINS="username"
```

### 5. Запусти бота:

```bash
python bot.py
```



---

## 📞 Обратная связь
- ### Если вы нашли баг или хотите предложить улучшение свяжитесь с разработчиками по email: nmbnc2008@gmail.com
  ### По телегу: nabiev06
