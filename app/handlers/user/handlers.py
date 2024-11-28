import asyncio
import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from loguru import logger

from app.database.requests import Database
from app.FSM.fsm import FSMSettings, FSMModel
from aiogram.fsm.state import default_state
from app.keyboards.inline_keyboards import (
    get_settings_keyboard,
    get_hide_keyboard,
    get_choose_model_keyboard,
    get_approve_gpt4o_keyboard,
    get_approve_scenary_keyboard
)

from app.keyboards.reply_keyboards import (
    get_menu_keyboard
)

from app.service.helpers import get_gpt_response

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from app.lexicon.bot_lexicon import LEXICON_RU, LEXICON_EN

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
        welcome_text_ru = f"Добро пожаловать, <b>{fullname}</b>!"
        welcome_text_en = f"Welcome back, <b>{fullname}</b>!"
    else:
        welcome_text_ru = f"С возвращением, <b>{fullname}</b>!"
        welcome_text_en = f"Welcome, <b>{fullname}</b>!"

    settings = await Database.get_user_settings(user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    if cur_lang == 'ru':
        await message.answer(LEXICON_RU['start'].format(hello=welcome_text_ru), reply_markup=await get_menu_keyboard(lang='ru'))
    else:
        await message.answer(LEXICON_EN['start'].format(hello=welcome_text_en), reply_markup=await get_menu_keyboard(lang='en'))

    logger.info(f"User {username} (ID: {user_id}) started the bot.")

@router.message(F.text == "🤖 Изменить модель")
@router.message(F.text == "🤖 Change Model")
async def change_model(message: Message, state: FSMContext):
    """
    Обработчик команды /chat и сообщения "🤖 Изменить модель".
    Предлагает выбрать модель для чата.
    """
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    await state.set_state(FSMModel.choosing_model)

    if cur_lang == 'ru':
        prompt = "Выберите модель для чата:"
    else:
        prompt = "Choose a chat model:"

    await message.answer(prompt, reply_markup=await get_choose_model_keyboard(lang=cur_lang))
    logger.info(f"User (ID: {user_id}) is choosing a model with ChatGPT.")

@router.message(F.text == "⚙️ Настройки")
@router.message(F.text == "⚙️ Settings")
async def cmd_settings(message: Message, state: FSMContext):
    """
    Обработчик команды /settings.
    Показывает текущие настройки пользователя и предоставляет варианты изменения.
    """
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)

    if not settings:
        if settings.get('language') == 'en':
            await message.answer("Your profile was not found. Please use /start to register.")
        else:
            await message.answer("Ваш профиль не найден. Пожалуйста, используйте /start для регистрации.")
        return

    cur_lang = settings.get('language', 'ru')

    if cur_lang == 'ru':
        settings_text = "<b>Ваши текущие настройки:</b>\n\n"
    else:
        settings_text = "<b>Your current settings:</b>\n\n"

    keyboard = await get_settings_keyboard(lang=cur_lang)

    await message.answer(settings_text, reply_markup=keyboard)
    logger.info(f"User (ID: {user_id}) requested settings.")

@router.callback_query(F.data == 'change_language')
async def change_language(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для изменения языка пользователя.
    """
    user_id = callback.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    await callback.message.delete()

    await state.set_state(FSMSettings.waiting_for_language)

    if cur_lang == 'ru':
        await Database.set_user_setting(user_id=user_id, setting='language', value='en')
        new_lang = 'en'
        response_text = "Language changed to EN."
        await callback.message.answer("<b>Your current settings:</b>\n\n", reply_markup=await get_settings_keyboard(lang='en'))
        await callback.message.answer("Settings have been changed", reply_markup=await get_menu_keyboard(lang='en'))
    else:
        await Database.set_user_setting(user_id=user_id, setting='language', value='ru')
        new_lang = 'ru'
        response_text = "Язык изменен на RU."
        await callback.message.answer("<b>Ваши текущие настройки:</b>\n\n", reply_markup=await get_settings_keyboard(lang='ru'))
        await callback.message.answer("Настройки были изменены", reply_markup=await get_menu_keyboard(lang='ru'))

    await callback.answer(text=response_text)
    logger.info(f"User (ID: {user_id}) changed language to {new_lang.upper()}.")

@router.callback_query(F.data == "hide")
async def callback_hide(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отмены текущего действия.
    """
    user_id = callback.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)

    if state.get_state() not in (FSMModel.waiting_for_message_gpt4o, FSMModel.waiting_for_message_scenary):
        await state.clear()

    await callback.message.delete()

    logger.info(f"User (ID: {user_id}) hided the action.")

    await callback.answer()

@router.callback_query(F.data.startswith("choice_"), StateFilter(FSMModel.choosing_model))
async def callback_choose_model(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора модели для чата.
    """
    model = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    if model == "gpt4o":
        if cur_lang == 'ru':
            text = LEXICON_RU['gpt4o_choice']
        else:
            text = LEXICON_EN['gpt4o_choice']
        keyboard = await get_approve_gpt4o_keyboard(lang=cur_lang)
    elif model == "scenary":
        if cur_lang == 'ru':
            text = LEXICON_RU['scenary_choice']
        else:
            text = LEXICON_EN['scenary_choice']
        keyboard = await get_approve_scenary_keyboard(lang=cur_lang)
    else:
        if cur_lang == 'ru':
            text = "Неизвестная модель."
        else:
            text = "Unknown model."
        keyboard = InlineKeyboardMarkup()

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    logger.info(f"User (ID: {user_id}) is approving model {model}.")

@router.callback_query(F.data.startswith("approve"), StateFilter(FSMModel.choosing_model))
async def callback_approve_model(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения выбора модели для чата.
    """
    model = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    success = await Database.set_user_setting(user_id=user_id, setting="chat_model", value=model)
    if success:
        if model == "gpt4o":
            if cur_lang == 'ru':
                text = "Модель GPT4o успешно выбрана."
            else:
                text = "GPT4o model has been successfully selected."
        elif model == "scenary":
            if cur_lang == 'ru':
                text = "Режим «сценарный» успешно выбран."
            else:
                text = "Scenary mode has been successfully selected."
        else:
            if cur_lang == 'ru':
                text = "Неизвестная модель."
            else:
                text = "Unknown model."

        await callback.message.edit_text(text)
        logger.info(f"User (ID: {user_id}) changed chat model to {model}.")
    else:
        if cur_lang == 'ru':
            text = "Не удалось изменить модель. Попробуйте позже."
        else:
            text = "Failed to change the model. Please try again later."
        await callback.message.edit_text(text)
        logger.error(f"Failed to change chat model for user (ID: {user_id}).")

    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "refuse")
async def callback_refuse_model(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отказа от выбора модели для чата.
    """
    user_id = callback.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    await state.clear()

    if cur_lang == 'ru':
        text = "Выбор модели отменен."
    else:
        text = "Model selection canceled."

    await callback.message.edit_text(text)
    await callback.answer()
    logger.info(f"User (ID: {user_id}) refused to choose a model.")

@router.message(Command("chat"))
@router.message(F.text == "🗨️ Запустить чат")
@router.message(F.text == "🗨️ Start Chat")
async def cmd_chat_start(message: Message, state: FSMContext):
    """
    Обработчик сообщения "🗨️ Запустить чат" и команды "/chat".
    Переводит пользователя в состояние ожидания сообщения для ChatGPT.
    """
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    model = await Database.get_user_model(user_id=user_id)

    if model == "gpt4o":
        full_model = "GPT4o"
        await state.set_state(FSMModel.waiting_for_message_gpt4o)
    elif model == "scenary":
        full_model = "Scenary"
        await state.set_state(FSMModel.waiting_for_message_scenary)
    else:
        # Default model
        full_model = "GPT4o"
        await state.set_state(FSMModel.waiting_for_message_gpt4o)

    if cur_lang == 'ru':
        prompt = f"Вы сейчас используете: {full_model}\n\nВведите ваше сообщение:"
    else:
        prompt = f"You are now using: {full_model}\n\nEnter your message:"

    await message.answer(prompt, reply_markup=await get_hide_keyboard(lang=cur_lang))

    logger.info(f"User (ID: {user_id}) is starting a chat with ChatGPT.")

@router.message(StateFilter(FSMModel.waiting_for_message_gpt4o))
async def process_gpt4o_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с GPT4o.
    """
    user_message = message.text
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с ChatGPT API
    # Пример:
    # gpt_response = await get_gpt_response(user_message)
    gpt_response = await get_gpt_response(user_message)

    await message.answer(gpt_response)
    logger.info(f"Response sent to user (ID: {user_id}): {gpt_response}")


@router.message(StateFilter(FSMModel.waiting_for_message_scenary))
async def process_scenary_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с Scenary.
    """

    # Загрузка JSON-файла с ответами при инициализации бота
    with open('app/lexicon/replies.json', 'r', encoding='utf-8') as f:
        RESPONSES = json.load(f)

    # Предобработка ключевых слов для ускорения поиска
    # Создадим список кортежей (список ответов с их ключевыми словами)
    # Это позволит сохранять порядок при проверке
    RESPONSE_LIST = []
    for response_key, response_value in RESPONSES.items():
        keywords = [kw.lower() for kw in response_value.get('keywords', [])]
        reply = response_value.get('reply', '')
        RESPONSE_LIST.append((keywords, reply))

    response = None

    # Если поддерживаются разные языки, можно добавить условие
    # Например, если RESPONSES разделены по языкам
    # В данном случае предполагается, что JSON на русском

    # Поиск соответствующего ответа по ключевым словам
    for keywords, reply in RESPONSE_LIST:
        for keyword in keywords:
            if keyword.lower() in message.text.lower():
                response = reply
                logger.info(f"Keyword '{keyword}' matched. Sending reply: {reply}")
                break  # Выход из внутреннего цикла
        if response:
            break  # Выход из внешнего цикла, если найден ответ
    else:
        response = "Я не знаю, как на это отвечать :("

    user_message = message.text
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с Scenary API или другим сервисом
    # Пример:
    # scenary_response = await get_scenary_response(user_message)
    scenary_response = "This is a sample response from Scenary." if cur_lang == 'en' else "Это пример ответа от Scenary."

    await message.answer(response)
    logger.info(f"Response sent to user (ID: {user_id}): {scenary_response}")


@router.message(StateFilter(FSMModel.scenary_processing_message))
async def fallback_handler(message: Message, state: FSMContext):
    """
    Обработчик для непредвиденных состояний.
    """
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    if cur_lang == 'ru':
        fallback_text = "Я не знаю, как на это отвечать :("
    else:
        fallback_text = "I don't know how to respond to that :("

    await message.answer(fallback_text)
    logger.error(f"Unexpected state while processing a message from user (ID: {user_id}).")
    await state.clear()
