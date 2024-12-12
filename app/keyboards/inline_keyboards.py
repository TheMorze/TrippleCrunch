from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def get_settings_keyboard(lang: str = 'ru', is_admin = False) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для настроек пользователя с динамической кнопкой языка.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками настроек.
    """
    if lang == 'ru':
        language_button_text = "Язык: 🇷🇺 Русский"
        admin_panel = "Войти в админ-панель"
        hide_button_text = "Скрыть"
    else:
        language_button_text = "Language: 🇬🇧 English"
        admin_panel = "Enter Admin Panel"
        hide_button_text = "Hide"

    if is_admin:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=language_button_text, callback_data="change_language")
                ],
                [
                    InlineKeyboardButton(text=admin_panel, callback_data="enter_admin_panel")],
                [
                    InlineKeyboardButton(text=hide_button_text, callback_data="hide")
                ]
            ]
        )
        return keyboard

    else:
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


async def get_choose_model_keyboard(gpt4o=True, scenary=True, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для выбора модели.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками выбора модели.
    """
    if lang == 'ru':
        gpt4o_text = "🚀 GPT4o"
        scenary_text = "👾 Сценарная"
        hide_text = "Скрыть"
    else:
        gpt4o_text = "🚀 GPT4o"
        scenary_text = "👾 Scenary"
        hide_text = "Hide"

    models = []
    if gpt4o:
        models.append(InlineKeyboardButton(text=gpt4o_text, callback_data="choice_gpt4o"))
    if scenary:
        models.append(InlineKeyboardButton(text=scenary_text, callback_data="choice_scenary"))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            models,
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

async def get_admin_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для администратора.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками администратора.
    """
    if lang == 'ru':
        find_user = "Найти пользователя"
        hide_text = "Скрыть"
    else:
        find_user = "Find User"
        hide_text = "Hide"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=find_user, callback_data="find_user")
            ],

            [
                InlineKeyboardButton(text=hide_text, callback_data="hide")
            ]
        ]
    )
    return keyboard

async def get_admin_user_editing_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для редактирования пользователя администратором.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками редактирования пользователя.
    """
    if lang == 'ru':
        change_model = "Изменить настройки доступа к моделям"
        change_token_balance = "Изменить баланс токенов"
        give_ban = "Выдать бан"
        hide_text = "Скрыть"
    else:
        change_model = "Change access setting to the models"
        change_token_balance = "Change token balance"
        give_ban = "Give ban"
        hide_text = "Hide"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=change_model, callback_data="change_user_model")
            ],

            [
                InlineKeyboardButton(text=change_token_balance, callback_data="change_user_token_balance")
            ],

            [
                InlineKeyboardButton(text=give_ban, callback_data="give_ban")
            ],

            [
                InlineKeyboardButton(text=hide_text, callback_data="hide")
            ]
        ]
    )
    return keyboard

async def get_user_model_access_keyboard(gpt = False, scenary = False, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для выбора модели чата.

    :param lang: Язык пользователя ('ru' или 'en').
    :return: Объект InlineKeyboardMarkup с кнопками выбора модели.
    """
    if lang == 'ru':
        if gpt:
            gpt4o_text = "✅ GPT4o"
        else:
            gpt4o_text = "❌ GPT4o"

        if scenary:
            scenary_text = "✅ Сценарный"
        else:
            scenary_text = "❌ Сценарный"

        hide_text = "Скрыть"
    else:
        if gpt:
            gpt4o_text = "✅ GPT4o"
        else:
            gpt4o_text = "❌ GPT4o"

        if scenary:
            scenary_text = "✅ Scenary"
        else:
            scenary_text = "❌ Scenary"

        hide_text = "Hide"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=gpt4o_text, callback_data="access_gpt4o"),
                InlineKeyboardButton(text=scenary_text, callback_data="access_scenary"),
            ],
            [
                InlineKeyboardButton(text=hide_text, callback_data="hide")
            ]
        ]
    )
    return keyboard
