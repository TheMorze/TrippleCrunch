from aiogram.types import ReplyKeyboardMarkup, \
                          KeyboardButton

async def get_menu_keyboard(one_time: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text='🗿 Хочу мем!'), KeyboardButton(text='📩 Загрузить мем')],
        [KeyboardButton(text='📊 Статистика'), KeyboardButton(text='🏆 Список лидеров')],
        [KeyboardButton(text='⚙️ Настройки')]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=one_time,
    )
