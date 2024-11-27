from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_menu_keyboard(one_time: bool = False) -> ReplyKeyboardMarkup:
    """
    Создание главной клавиатуры меню для GPT-бота.

    :param one_time: Флаг для отображения клавиатуры один раз.
    :return: Объект ReplyKeyboardMarkup с кнопками меню.
    """
    keyboard = [
        [KeyboardButton(text='🗨️ Запустить чат'), KeyboardButton(text='⚙️ Настройки')],
        [KeyboardButton(text='❓ Помощь'), KeyboardButton(text='📄 FAQ')]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=one_time,
    )
