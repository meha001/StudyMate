# Импортируем ЭКЗЕМПЛЯРЫ роутеров
from .admin_side import admin_router
from .user_side import router

__all__ = ['admin_router', 'router']