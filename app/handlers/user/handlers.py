import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from loguru import logger

from app.database.requests import Database
from app.FSM.fsm import FSMSettings, FSMChatGPT
from app.keyboards.inline_keyboards import (
    get_settings_keyboard,
    get_change_language_keyboard,
    get_change_theme_keyboard,
    get_cancel_keyboard
)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Регистрирует пользователя в базе данных и приветствует его.
    """
    user_id = message.from_user.id
    username = message.from_user.username or ""
    fullname = message.from_user.full_name or ""

    user, created = await Database.add_user(user_id=user_id, username=username, fullname=fullname)
    if not created:
        welcome_text = f"Добро пожаловать, {fullname}!\nВаш профиль был успешно создан."
    else:
        welcome_text = f"С возвращением, {fullname}!\nВаш профиль уже существует."

    await message.answer(welcome_text)
    logger.info(f"User {username} (ID: {user_id}) started the bot.")

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """
    Обработчик команды /settings.
    Показывает текущие настройки пользователя и предоставляет варианты изменения.
    """
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)

    if not settings:
        await message.answer("Ваш профиль не найден. Пожалуйста, используйте /start для регистрации.")
        return

    notifications_status = 'Включены' if settings['notifications_enabled'] else 'Выключены'
    settings_text = (
        f"Ваши настройки:\n"
        f"Язык: {settings['language']}\n"
        f"Уведомления: {notifications_status}\n"
        f"Тема: {settings['theme']}\n\n"
        f"Выберите, что хотите изменить:"
    )

    # Получение клавиатуры из inline_keyboards.py с учётом текущего состояния уведомлений
    keyboard = await get_settings_keyboard(notifications_enabled=settings['notifications_enabled'])

    await message.answer(settings_text, reply_markup=keyboard)
    logger.info(f"User (ID: {user_id}) requested settings.")

@router.callback_query(F.data == "change_language")
async def callback_change_language(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для изменения языка пользователя.
    """
    await state.set_state(FSMSettings.waiting_for_language)
    keyboard = await get_change_language_keyboard()
    await callback.message.answer(
        "Пожалуйста, выберите язык:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_language_"), StateFilter(FSMSettings.waiting_for_language))
async def callback_set_language(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик установки выбранного языка.
    """
    language = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    success = await Database.set_user_setting(user_id=user_id, setting="language", value=language)
    if success:
        language_full = "Русский" if language == "ru" else "Английский"
        await callback.message.edit_text(f"Язык успешно изменен на {language_full}.")
        logger.info(f"User (ID: {user_id}) changed language to {language}.")
    else:
        await callback.message.edit_text("Не удалось изменить язык. Попробуйте позже.")
        logger.error(f"Failed to change language for user (ID: {user_id}).")

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "change_theme")
async def callback_change_theme(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для изменения темы пользователя.
    """
    await state.set_state(FSMSettings.waiting_for_theme)
    keyboard = await get_change_theme_keyboard()
    await callback.message.answer(
        "Пожалуйста, выберите тему:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_theme_"), StateFilter(FSMSettings.waiting_for_theme))
async def callback_set_theme(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик установки выбранной темы.
    """
    theme = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    success = await Database.set_user_setting(user_id=user_id, setting="theme", value=theme)
    if success:
        theme_full = "Светлая" if theme == "light" else "Тёмная"
        await callback.message.edit_text(f"Тема успешно изменена на {theme_full}.")
        logger.info(f"User (ID: {user_id}) changed theme to {theme}.")
    else:
        await callback.message.edit_text("Не удалось изменить тему. Попробуйте позже.")
        logger.error(f"Failed to change theme for user (ID: {user_id}).")

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "toggle_notifications")
async def callback_toggle_notifications(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для переключения уведомлений пользователя.
    """
    user_id = callback.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)

    if not settings:
        await callback.message.answer("Ваш профиль не найден. Пожалуйста, используйте /start для регистрации.")
        await callback.answer()
        return

    new_status = not settings["notifications_enabled"]
    success = await Database.set_user_setting(user_id=user_id, setting="notifications_enabled", value=new_status)

    if success:
        # Обновление текста кнопки уведомлений с соответствующим эмодзи
        notifications_text = "Уведомления включены ✅" if new_status else "Уведомления выключены ❌"
        # Создание новой клавиатуры с обновлённой кнопкой уведомлений
        updated_keyboard = InlineKeyboardMarkup(
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
        await callback.message.edit_reply_markup(reply_markup=updated_keyboard)
        status_text = "включены" if new_status else "отключены"
        await callback.answer(f"Уведомления были изменены успешно: {status_text}")
        logger.info(f"User (ID: {user_id}) {status_text} notifications.")
    else:
        await callback.message.answer("Failed to change notification settings. Please try again later.")
        logger.error(f"Failed to change notification settings for user (ID: {user_id}).")
        await callback.answer()

@router.callback_query(F.data == "cancel", StateFilter("*"))
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отмены текущего действия.
    """
    await state.clear()
    await callback.message.edit_text("Action canceled.")
    logger.info(f"User (ID: {callback.from_user.id}) canceled the action.")
    await callback.answer()

@router.message(Command("chat"))
async def cmd_chat(message: Message, state: FSMContext):
    """
    Обработчик команды /chat для начала взаимодействия с ChatGPT.
    """
    await state.set_state(FSMChatGPT.waiting_for_message)
    await message.answer("Привет! Спроси меня любой вопрос — и я помогу тебе.")
    logger.info(f"User (ID: {message.from_user.id}) started a chat with ChatGPT.")

@router.message(StateFilter(FSMChatGPT.waiting_for_message))
async def process_chat_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с ChatGPT.
    """
    user_message = message.text
    user_id = message.from_user.id

    await state.set_state(FSMChatGPT.processing_message)
    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с ChatGPT API
    # Пример:
    # gpt_response = await get_gpt_response(user_message)
    gpt_response = "This is a sample response from ChatGPT."

    await message.answer(gpt_response)
    logger.info(f"Response sent to user (ID: {user_id}): {gpt_response}")

    await state.clear()

@router.message(StateFilter(FSMChatGPT.processing_message))
async def fallback_handler(message: Message, state: FSMContext):
    """
    Обработчик для непредвиденных состояний.
    """
    await message.answer("Я не знаю, как на это отвечать :(")
    logger.error(f"Unexpected state while processing a message from user (ID: {message.from_user.id}).")
    await state.clear()
