from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def get_menu_keyboard(one_time: bool = False, lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Создание главной клавиатуры меню для GPT-бота с поддержкой нескольких языков.

    :param one_time: Флаг для отображения клавиатуры один раз.
    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект ReplyKeyboardMarkup с кнопками меню.
    """

    # Определение текстов кнопок на основе выбранного языка
    if lang == 'ru':
        start_chat_text = '🗨️ Запустить чат'
        change_model_text = '🤖 Изменить модель'
        settings_text = '⚙️ Настройки'
        flag = '🇷🇺'
    else:
        start_chat_text = '🗨️ Start Chat'
        change_model_text = '🤖 Change Model'
        settings_text = '⚙️ Settings'
        flag = '🇬🇧'

    # Создание клавиатуры с динамическими текстами кнопок
    keyboard = [
        [KeyboardButton(text=start_chat_text)],
        [KeyboardButton(text=change_model_text), KeyboardButton(text=settings_text)],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=one_time,
    )
