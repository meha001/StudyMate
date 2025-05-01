from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup # type: ignore

def group_keyboard(group_list: list) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=group[0])] for group in group_list
    ], resize_keyboard=True)
    return kb

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # type: ignore

from aiogram.utils.keyboard import InlineKeyboardBuilder # type: ignore
from aiogram.types import InlineKeyboardButton # type: ignore


def group_keyboard(group_list: list) -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопками групп из списка."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=group[0])] for group in group_list],
        resize_keyboard=True
    )

def user_main_menu() -> InlineKeyboardMarkup:
    """Основное меню с кнопками: расписание, новости, вопросы."""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="📅 Моё расписание", callback_data="user_schedule"))
    builder.row(InlineKeyboardButton(text="📰 Новости", callback_data="user_news"))
    builder.row(InlineKeyboardButton(text="❓ Вопрос", callback_data="user_question"))

    return builder.as_markup()
