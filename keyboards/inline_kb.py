from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # type: ignore



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # type: ignore



async def create_reply_keyboard(user_id: int, question_id: int) -> InlineKeyboardMarkup:
    """Создает кнопку ответа на вопрос пользователя"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Ответить", 
                    callback_data=f"reply_{user_id}_{question_id}"
                )
            ]
        ]
    )

def create_delete_news_keyboard(news_date: str) -> InlineKeyboardMarkup:
    """Создает кнопку для удаления новости"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Удалить новость",
                    callback_data=f"delete_news_{news_date}"
                )
            ]
        ]
    )
