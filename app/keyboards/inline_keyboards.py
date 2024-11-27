from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests import Database
from loguru import logger


async def get_settings_keyboard(notifications_enabled: bool):
    """
    Создание клавиатуры для настроек пользователя с динамической кнопкой уведомлений.
    """
    notifications_text = "Уведомления включены ✅" if notifications_enabled else "Уведомления выключены ❌"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить язык", callback_data="change_language"),
                InlineKeyboardButton(text="Изменить тему", callback_data="change_theme"),
            ],
            [
                InlineKeyboardButton(text=notifications_text, callback_data="toggle_notifications"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="back")
            ]
        ]
    )
    return keyboard


async def get_change_language_keyboard():
    """
    Создание клавиатуры для выбора языка.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="set_language_ru"),
                InlineKeyboardButton(text="Английский", callback_data="set_language_en"),
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    return keyboard


async def get_choose_model_keyboard():
    """
    Создание клавиатуры для выбора языка.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="GPT4o", callback_data="choice_gpt4o"),
                InlineKeyboardButton(text="Сценарный", callback_data="choice_scenary"),
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    return keyboard

async def get_change_theme_keyboard():
    """
    Создание клавиатуры для выбора темы.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Светлая", callback_data="set_theme_light"),
                InlineKeyboardButton(text="Тёмная", callback_data="set_theme_dark"),
            ],
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    return keyboard


async def get_cancel_keyboard():
    """
    Создание клавиатуры для отмены действия.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    return keyboard
