from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def get_settings_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для настроек пользователя с динамической кнопкой языка.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками настроек.
    """
    if lang == 'ru':
        language_button_text = "Язык: 🇷🇺 Русский"
        hide_button_text = "Скрыть"
    else:
        language_button_text = "Language: 🇬🇧 English"
        hide_button_text = "Hide"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=language_button_text, callback_data="change_language"),
            ],
            [
                InlineKeyboardButton(text=hide_button_text, callback_data="hide")
            ]
        ]
    )
    return keyboard


async def get_choose_model_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для выбора модели.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками выбора модели.
    """
    if lang == 'ru':
        gpt4o_text = "🚀 GPT4o"
        scenary_text = "👾 Сценарный"
        llama3_text = "🦙 Llama3"
        hide_text = "Скрыть"
    else:
        gpt4o_text = "🚀 GPT4o"
        scenary_text = "👾 Scenary"
        llama3_text = "🦙 Llama3"
        hide_text = "Hide"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=gpt4o_text, callback_data="choice_gpt4o"),
                InlineKeyboardButton(text=llama3_text, callback_data="choice_llama3"),
                InlineKeyboardButton(text=scenary_text, callback_data="choice_scenary"),

            ],
            [
                InlineKeyboardButton(text=hide_text, callback_data="hide")
            ]
        ]
    )
    return keyboard


async def get_approve_gpt4o_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для подтверждения выбора модели GPT4o.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками подтверждения.
    """
    if lang == 'ru':
        yes_text = "✅ Да"
        no_text = "❌ Нет"
    else:
        yes_text = "✅ Yes"
        no_text = "❌ No"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data="approve_gpt4o"),
                InlineKeyboardButton(text=no_text, callback_data="refuse")
            ]
        ]
    )
    return keyboard


async def get_approve_llama3_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для подтверждения выбора модели Llama3.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками подтверждения.
    """
    if lang == 'ru':
        yes_text = "✅ Да"
        no_text = "❌ Нет"
    else:
        yes_text = "✅ Yes"
        no_text = "❌ No"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data="approve_llama3"),
                InlineKeyboardButton(text=no_text, callback_data="refuse")
            ]
        ]
    )
    return keyboard

async def get_approve_scenary_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для подтверждения выбора модели Сценарный.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками подтверждения.
    """
    if lang == 'ru':
        yes_text = "✅ Да"
        no_text = "❌ Нет"
    else:
        yes_text = "✅ Yes"
        no_text = "❌ No"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data="approve_scenary"),
                InlineKeyboardButton(text=no_text, callback_data="hide")
            ]
        ]
    )
    return keyboard


async def get_hide_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для отмены действия.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопкой отмены.
    """
    if lang == 'ru':
        hide_text = "Скрыть"
    else:
        hide_text = "Hide"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=hide_text, callback_data="hide")
            ]
        ]
    )
    return keyboard
