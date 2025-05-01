from aiogram import F, Router # type: ignore
from aiogram.enums import ParseMode # type: ignore
from aiogram.exceptions import TelegramAPIError # type: ignore
from aiogram.filters import Command # type: ignore
from aiogram.fsm.context import FSMContext # type: ignore
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message, ReplyKeyboardRemove, Union # type: ignore
from aiogram.utils.keyboard import InlineKeyboardBuilder # type: ignore

import html

from create_bot import ADMINS, bot
from data_base import sqlite_db
from keyboards import inline_kb, usually_kb

from keyboards.usually_kb import  user_main_menu
from .states import AskQuestionStates, AdminScheduleStates, SelectGroupStates, StartStates

router = Router()




#=========================START=================================
@router.message(Command("start"))
async def cmd_start(message: Message):
    
    await message.answer(
        "👋 Привет! Я бот для студентов.\n\n"
        "📌 Что умею:\n"
        "— Показывать расписание\n"
        "— Присылать новости\n"
        "— Передавать вопросы администраторам\n\n"
        "ℹ️ Посмотреть команды: /help\n"
        "👇 Выбери действие с помощью кнопок:",
        reply_markup=user_main_menu()
    )

@router.callback_query(F.data == "user_schedule")
async def handle_schedule(callback: CallbackQuery):
    await callback.answer()

    group = await sqlite_db.get_user_group(callback.from_user.id)
    if not group or group == "no_group":
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Выбрать группу", callback_data="select_group"))
        await callback.message.answer("❗ Сначала выбери группу:", reply_markup=builder.as_markup())
        return

    schedule = await sqlite_db.get_group(group)
    if not schedule or not schedule[0][1]:
        await callback.message.answer("📭 Расписание для вашей группы ещё не добавлено.")
        return

    await callback.message.answer_photo(
        photo=schedule[0][1],
        caption=f"📅 Расписание группы {group}"
    )
    
        

       
#==========================GROUP=========================================================
@router.message(StartStates.group_name)
async def start_state(message: Message, state: FSMContext):
    all_group_names = [_[0] for _ in await sqlite_db.get_all_groups()]
    if message.text in all_group_names:
        await sqlite_db.change_user_group(message.from_user.id, message.text)
        await message.answer(
            f'Окей, прикрепил тебя к группе {message.text}',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            'Ты пропустил выбор группу, но всегда сможешь выбрать ее с помощью /select_group',
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()


async def select_group_handler(update: Union[Message, CallbackQuery]):
    """Общий обработчик выбора группы"""
    if isinstance(update, CallbackQuery):
        await update.answer()
        message = update.message
    else:
        message = update
    
    groups = await sqlite_db.get_all_groups()
    if not groups:
        await message.answer("ℹ️ Нет доступных групп")
        return
    
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(text=group[0], callback_data=f"set_group_{group[0]}")
    builder.adjust(2)
    
    await message.answer("Выберите группу:", reply_markup=builder.as_markup())

@router.message(Command("select_group"))
async def select_group_cmd(message: Message):
    if message.from_user.username not in ADMINS: 
        await message.delete()
    await select_group_handler(message)

@router.callback_query(F.data == "select_group")
async def select_group_btn(callback: CallbackQuery):
    await select_group_handler(callback)

@router.callback_query(F.data.startswith("set_group_"))
async def set_group_handler(callback: CallbackQuery):
    group_name = callback.data.split('_')[-1]
    await sqlite_db.change_user_group(callback.from_user.id, group_name)
    await callback.answer(f"✅ Группа {group_name} выбрана!", show_alert=True)
    
    await callback.message.delete()

@router.message(SelectGroupStates.group_name)
async def select_group_state(message: Message, state: FSMContext):
    all_group_names = [_[0] for _ in await sqlite_db.get_all_groups()]
    if message.text in all_group_names:
        await sqlite_db.change_user_group(message.from_user.id, message.text)
        await message.answer(
            'Группа группа успешно выбрана',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            'Группу которую вы выбрали, не существует',
            reply_markup=ReplyKeyboardRemove()
        )
    

@router.message(Command("delete_me_from_group"))
async def delete_from_group(message: Message):
    await message.delete()
    await sqlite_db.change_user_group(message.from_user.id, None)
    await message.answer('Группа успешно отвязана')


#==========================NEWS==========================================
@router.callback_query(F.data == "user_news")
async def show_news(callback: CallbackQuery):
    await callback.answer()
    news = await sqlite_db.get_news()
    if not news:
        return await callback.answer("📭 Сейчас нет новостей", show_alert=True)

    for item in news[:3]:
        caption = (
            f"📰 <b>{item[1]}</b>\n\n"
            f"{item[2][:200]}{'...' if len(item[2]) > 200 else ''}\n"
            f"{item[4].strftime('%d.%m.%Y') if len(item) > 4 else ''}"
        )
        await callback.message.answer_photo(
            photo=item[3],
            caption=caption,
            parse_mode="HTML"
        )

@router.message(Command("news"))
async def news_command(message: Message):
    await message.delete()
    news = await sqlite_db.get_news()
    if message.chat.username not in ADMINS:
        for item in news[:3]:  # Показываем 3 последние новости
            try:
                
                await message.answer_photo(
                    photo=item[3],
                    caption=f"НОВОСТЬ\n\n{item[1]}\n\n{item[2]}"
                )
                
            except Exception as e:
                print(f"Ошибка при отправке новости: {e}")
    else:
        for item in news:
            try:
                await message.answer_photo(
                    photo=item[3],
                    caption=f"НОВОСТЬ\n\n{item[1]}\n\n{item[2]}"
                )

            except Exception as e:
                print(f"Ошибка при отправке новости: {e}")


#===========================================QUESTIONS===============================================================
async def ask_question_handler(message_or_callback: Union[Message, CallbackQuery], state: FSMContext):
    """Общий обработчик для команды и кнопки вопроса"""
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.answer()
        message = message_or_callback.message
    else:
        message = message_or_callback
    
    await message.answer("✍️ Напишите ваш вопрос\n (Ваш вопрос должен состоять из двух или более слов. Пожалуйста, формулируйте предложение чётко и ясно.):")
    await state.set_state(AskQuestionStates.get_question)

@router.message(Command("ask_question"))
async def ask_question_command(message: Message, state: FSMContext):
    
    await ask_question_handler(message, state)


@router.callback_query(F.data == "user_question")
async def ask_question_btn(callback: CallbackQuery, state: FSMContext):
    await ask_question_handler(callback, state)



@router.message(AskQuestionStates.get_question)
async def get_question_state(message: Message, state: FSMContext):
    if len(message.text.split()) <= 1:
        return await message.answer("❗Вопрос незадан\n\n (Ваш вопрос должен состоять из двух или более слов. Пожалуйста, формулируйте предложение чётко и ясно.)")
    await state.update_data({
        'user_id': message.from_user.id,
        'question': message.text,
        'nick': message.from_user.username
    })
    data = await state.get_data()
    await sqlite_db.add_question(data)
    await message.answer("Вопрос задан, ждите ответа...")
    await state.clear()


async def add_proxy_data(state: FSMContext, data: dict):
    await state.update_data(data)

#=============================================ID=======================================================
@router.message(Command("id"))
async def get_group_id(message: Message):
    await message.delete()
    await message.answer(str(message.chat.id))


#============================================SCHEDULE==================================================
async def schedule_handler(update: Union[Message, CallbackQuery], state: FSMContext):
    """Общий обработчик для расписания"""
    message = update if isinstance(update, Message) else update.message
    
    is_admin = message.from_user.username in ADMINS if message.from_user.username else False
    
    if not is_admin:
        user_group = await sqlite_db.get_user_group(message.from_user.id)
        if not user_group or user_group == "no_group":
            await message.answer("ℹ️ Сначала выберите группу через /select_group")
            return
            
        group_data = await sqlite_db.get_group(user_group)
        if not group_data or not group_data[0][1]:
            await message.answer("📭 Расписание для вашей группы ещё не добавлено")
            return
            
        await message.answer_photo(
            photo=group_data[0][1],
            caption=f"📅 Расписание группы {user_group}"
        )
    else:
        all_groups = await sqlite_db.get_all_groups()
        if not all_groups:
            await message.answer("ℹ️ Нет доступных групп")
            return
            
        builder = InlineKeyboardBuilder()
        for group in all_groups:
            builder.button(text=group[0], callback_data=f"schedule_{group[0]}")
        builder.adjust(2)
        
        await message.answer(
            "👑 Выберите группу:",
            reply_markup=builder.as_markup()
        )

@router.message(Command("schedule", "расписание"))
async def schedule_command(message: Message, state: FSMContext):
    if message.from_user.username not in ADMINS:
        await message.delete()
    await schedule_handler(message, state)


@router.callback_query(F.data.startswith("schedule_"))
async def process_admin_group_selection(callback: CallbackQuery):
    group_name = callback.data.split("_")[1]
    group_data = await sqlite_db.get_group(group_name)
    
    if not group_data or not group_data[0][1]:
        await callback.answer(f"Расписание для группы {group_name} ещё не добавлено", show_alert=True)

    else:
        await callback.answer()
        await callback.message.answer_photo(
            photo=group_data[0][1],
            caption=f"📅 Расписание группы {group_name}"
        )
