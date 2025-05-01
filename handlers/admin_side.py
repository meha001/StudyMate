from aiogram import Router, F # type: ignore
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove # type: ignore
from aiogram.filters import Command # type: ignore
from aiogram.fsm.context import FSMContext # type: ignore
from aiogram.enums import ParseMode # type: ignore
from aiogram.utils.keyboard import InlineKeyboardBuilder # type: ignore
from aiogram.utils.markdown import hbold, hitalic # type: ignore
from aiogram.enums import ParseMode # type: ignore
from aiogram.exceptions import TelegramAPIError # type: ignore
from keyboards import usually_kb, inline_kb
from data_base import sqlite_db
from .states import (
    NewsStates, 
    CreateGroupStates, 
    DeleteGroupStates, 
    ScheduleStates, 
    DeleteScheduleStates, 
    AnswerTheQuestion,
    AnswerStates
)
from create_bot import ADMINS 
from datetime import datetime
from handlers.sending_messages import sending_schedule  # Добавляем импорт


from config import is_admin_sync, get_admins_sync, add_admin_sync, remove_admin_sync, count_admins_sync
import asyncio


admin_router = Router()

# Группы
@admin_router.message(Command("create_group"))
async def create_group_command(message: Message, state: FSMContext):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")
    await message.answer("📥 Введите название новой группы:")
    await state.set_state(CreateGroupStates.group_name)


@admin_router.message(CreateGroupStates.group_name)
async def create_group_state(message: Message, state: FSMContext):
    try:
        await sqlite_db.add_group(message.text, message)
        await message.answer("✅ Группа успешно создана!", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании группы: {e}")
    await state.clear()


@admin_router.message(Command("delete_group"))
async def delete_group_command(message: Message, state: FSMContext):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")
    groups = await sqlite_db.get_all_groups()
    await message.answer(
        "🗑 Выберите группу, которую нужно удалить:",
        reply_markup=usually_kb.group_keyboard(groups)
    )
    await state.set_state(DeleteGroupStates.group_name)


@admin_router.message(DeleteGroupStates.group_name)
async def delete_group_state(message: Message, state: FSMContext):
    group_names = [name[0] for name in await sqlite_db.get_all_groups()]
    if message.text in group_names:
        await sqlite_db.delete_group(message.text)
        await message.answer("✅ Группа удалена.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("⚠️ Такой группы не найдено.")
    await state.clear()


@admin_router.message(Command("groups"))
async def list_groups(message: Message):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")

    groups = await sqlite_db.get_all_groups()
    if not groups:
        return await message.answer("📭 Группы пока не созданы.")

    group_list = "\n".join([f"• {g[0]}" for g in groups])
    await message.answer(f"📚 <b>Список всех групп:</b>\n\n{group_list}", parse_mode=ParseMode.HTML)



# Новости
@admin_router.message(Command("create_news"))
async def create_news(message: Message, state: FSMContext):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")
    await message.answer("📝 Введите заголовок новости:")
    await state.set_state(NewsStates.title)


@admin_router.message(NewsStates.title)
async def state_title_news(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📝 Теперь введите содержание новости:")
    await state.set_state(NewsStates.content)


@admin_router.message(NewsStates.content)
async def state_content_news(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer("🖼 Пришлите изображение для новости:")
    await state.set_state(NewsStates.image)


@admin_router.message(NewsStates.image, F.photo)
async def state_image_news(message: Message, state: FSMContext):
    data = await state.get_data()
    data['image'] = message.photo[-1].file_id
    await sqlite_db.add_news(data)
    await message.answer("✅ Новость успешно добавлена!")

    # Рассылка пользователям
    try:
        users = await sqlite_db.get_all_users()
        print(users)
        for user in users:
            user_id = user[0]
            try:
                
                await message.bot.send_photo(
                    chat_id=user_id,
                    photo=data['image'],
                    caption=f"<b>{data['title']}</b>\n\n{data['content']}",
                    parse_mode=ParseMode.HTML
                )
            except TelegramAPIError:
                continue
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при рассылке: {e}")

    await state.clear()


@admin_router.message(Command("delete_news"))
async def delete_news(message: Message):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")

    news = await sqlite_db.get_news()
    if not news:
        return await message.answer("📭 Нет доступных новостей.")

    for item in news:
        await message.answer_photo(
            photo=item[3],
            caption=f"<b>{item[1]}</b>\n\n{item[2]}",
            reply_markup=inline_kb.create_delete_news_keyboard(str(item[0])),
            parse_mode=ParseMode.HTML
        )


@admin_router.callback_query(F.data.startswith("delete_news_"))
async def process_delete_news(callback: CallbackQuery):
    news_date = callback.data.split("_")[2]
    await sqlite_db.delete_news(news_date)
    await callback.message.delete()
    await callback.answer("🗑 Новость удалена!", show_alert=True)

# Расписание
@admin_router.message(Command("create_schedule"))
async def create_schedule(message: Message, state: FSMContext):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")
    groups = await sqlite_db.get_all_groups()
    if not groups:
        return await message.answer("⚠️ Нет доступных групп. Сначала создайте группу через /create_group")

    await message.answer(
        "🗓 Выберите группу для добавления расписания:",
        reply_markup=usually_kb.group_keyboard(groups)
    )
    await state.set_state(ScheduleStates.select_group)


@admin_router.message(ScheduleStates.select_group)
async def state_select_group_schedule(message: Message, state: FSMContext):
    all_groups = [name[0] for name in await sqlite_db.get_all_groups()]
    if message.text in all_groups:
        await state.update_data(group=message.text)
        await message.answer("📤 Пришлите фотографию расписания:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(ScheduleStates.image)
    else:
        await message.answer("⚠️ Такой группы не найдено.")
        await state.clear()


@admin_router.message(ScheduleStates.image, F.photo)
async def state_image_schedule(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        if 'group' not in data:
            await message.answer("❌ Группа не выбрана. Попробуйте сначала.")
            await state.clear()
            return

        data['image'] = message.photo[-1].file_id
        await sqlite_db.create_schedule(data)

        await message.answer("✅ Расписание успешно добавлено!")
        await sending_schedule(data['group'])
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await state.clear()


@admin_router.message(Command("delete_schedule"))
async def delete_schedule(message: Message, state: FSMContext):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")

    groups = await sqlite_db.get_all_groups()
    await message.answer(
        "🗑 Выберите группу, расписание которой нужно удалить:",
        reply_markup=usually_kb.group_keyboard(groups)
    )
    await state.set_state(DeleteScheduleStates.select_group)


@admin_router.message(DeleteScheduleStates.select_group)
async def state_delete_schedule(message: Message, state: FSMContext):
    all_groups = [name[0] for name in await sqlite_db.get_all_groups()]
    if message.text in all_groups:
        await sqlite_db.delete_schedule(message.text)
        await message.answer(f"✅ Расписание группы {message.text} удалено.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("⚠️ Такой группы не найдено.")
    await state.clear()


# Вопросы от пользователей
@admin_router.message(Command("view_questions"))
async def view_questions(message: Message):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")

    questions = await sqlite_db.get_unanswered_questions_with_groups()
    if not questions:
        return await message.answer("📭 Нет новых вопросов от пользователей.")
    flag = 1
    for q in questions:
        if len(q[2].split()) > 1:
            flag = 0
            question_text = (
                f"📌 <b>Новый вопрос</b>\n"
                f"👤 <b>Студент:</b> @{q[3]}\n"
                f"🏫 <b>Группа:</b> {q[4] or 'не указана'}\n\n"
                f"📝 <b>Вопрос:</b>\n{q[2]}"
            )
            await message.answer(
                question_text,
                reply_markup=await inline_kb.create_reply_keyboard(user_id=q[1], question_id=q[0]),
                parse_mode=ParseMode.HTML
            )
    if flag:
        return await message.answer("📭 Нет новых вопросов от пользователей.")


@admin_router.callback_query(F.data.startswith("reply_"))
async def process_reply(callback: CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split('_')
        if len(parts) != 3:
            raise ValueError("Неверный формат данных для ответа.")

        user_id = int(parts[1])
        question_id = int(parts[2])

        await state.update_data(target_user_id=user_id, question_id=question_id)
        await state.set_state(AnswerStates.waiting_for_answer)

        await callback.message.answer("✍️ Введите ответ пользователю:")
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)


@admin_router.message(AnswerStates.waiting_for_answer)
async def send_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data['target_user_id']
    question_id = data['question_id']

    try:
        await message.bot.send_message(
            chat_id=target_user_id,
            text=f"📨 Ответ от администратора:\n{message.text}"
        )
        await sqlite_db.mark_question_as_answered(question_id)
        await message.answer("✅ Ответ отправлен, вопрос помечен как решённый.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке ответа: {e}")

    await state.clear()




# Команда /help


@admin_router.message(Command("help"))
async def help_command(message: Message):
    await message.delete()
    is_admin = message.from_user.username in ADMINS

    user_help = """
📚 <b>Список доступных команд:</b>

<b>Основное:</b>
/start — Перезапуск бота
/help — Справка

<b>Группа:</b>
/select_group — Выбрать группу
/schedule — Посмотреть расписание

<b>Новости:</b>
/news — Последние новости

<b>Вопрос:</b>
/ask_question — Задать вопрос администратору

<b>Профиль:</b>
/id — Узнать свой ID
/delete_me_from_group — Покинуть группу
"""

    admin_help = f"""
🛠 <b>Панель администратора:</b>

<b>Основное:</b>
/start — Перезапуск
/help — Помощь
/id — ID пользователя

<b>Управление администраторами:</b>
/add_admin [username] — Добавить админа
/remove_admin [username] — Удалить админа
/list_admins — Список админов

<b>Группы:</b>
/create_group — Создать группу
/delete_group — Удалить группу
/groups — Все группы

<b>Расписание:</b>
/create_schedule — Добавить расписание
/delete_schedule — Удалить расписание
/schedule — Посмотреть расписание

<b>Новости:</b>
/create_news — Добавить новость
/delete_news — Удалить новость
/news — Просмотр новостей

<b>Вопросы:</b>
/view_questions — Все вопросы
/ask_question — Ответить студенту
"""

    await message.answer(
        (admin_help if is_admin else user_help),
        parse_mode=ParseMode.HTML
    )


@admin_router.message(Command("add_admin"))
async def add_admin_command(message: Message):
    if not message.from_user.username:
        return await message.answer("❌ У вас отсутствует username в Telegram.")
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")

    args = message.text.split()
    if len(args) < 2:
        return await message.answer("❌ Используйте формат: /add_admin [username]")

    new_admin = args[1].lower().replace('@', '')
    await asyncio.to_thread(add_admin_sync, new_admin, message.from_user.username)
    await message.answer(f"✅ Пользователь @{new_admin} добавлен в администраторы.")


@admin_router.message(Command("list_admins"))
async def list_admins_command(message: Message):
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")
    await message.delete()
    admins = await asyncio.to_thread(get_admins_sync)
    text = "👑 <b>Список администраторов:</b>\n" + "\n".join(f"• @{a}" for a in admins)
    await message.answer(text, parse_mode=ParseMode.HTML)


@admin_router.message(Command("remove_admin"))
async def remove_admin_command(message: Message):
    if not message.from_user.username:
        return await message.answer("❌ У вас отсутствует username в Telegram.")
    if message.from_user.username not in ADMINS:
        return await message.answer("⛔ Команда доступна только администраторам.")

    args = message.text.split()
    if len(args) < 2:
        return await message.answer("❌ Используйте формат: /remove_admin [username]")

    target = args[1].lower().replace('@', '')
    if target == message.from_user.username.lower():
        return await message.answer("❌ Нельзя удалить самого себя!")

    if await asyncio.to_thread(count_admins_sync) <= 1:
        return await message.answer("❌ Вы не можете удалить последнего администратора!")

    if not is_admin_sync(target):
        return await message.answer(f"❌ Пользователь @{target} не является администратором.")

    await asyncio.to_thread(remove_admin_sync, target)
    await message.answer(f"✅ Пользователь @{target} удалён из администраторов.")
