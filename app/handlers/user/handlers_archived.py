import asyncio
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
    get_cancel_keyboard,
    get_choose_model_keyboard,
    get_approve_gpt4o_keyboard,
    get_approve_scenary_keyboard
)

from app.keyboards.reply_keyboards import (
    get_menu_keyboard
)

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from app.lexicon.bot_lexicon import LEXICON_RU


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
        welcome_text = f"Добро пожаловать, <b>{fullname}</b>!"
    else:
        welcome_text = f"С возвращением, <b>{fullname}</b>!"


    cur_lang = (await Database.get_user_settings(user_id))['language']
    await message.answer(LEXICON_RU['start'].format(hello=welcome_text), reply_markup=await get_menu_keyboard(lang=cur_lang))
    logger.info(f"User {username} (ID: {user_id}) started the bot.")

@router.message(Command("chat"))
@router.message(F.text == "🤖 Изменить модель")
async def cmd_chat(message: Message, state: FSMContext):
    """
    Обработчик сообщения "🗨️ Запустить чат" и команды "/chat".
    Предлагает выбрать модель для чата.
    """

    await state.set_state(FSMModel.choosing_model)

    await message.answer("Выберите модель для чата:", reply_markup=await get_choose_model_keyboard())
    logger.info(f"User (ID: {message.from_user.id}) is choosing a model with ChatGPT.")



@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: Message, state: FSMContext):
    """
    Обработчик команды /settings.
    Показывает текущие настройки пользователя и предоставляет варианты изменения.
    """
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)

    if not settings:
        await message.answer("Ваш профиль не найден. Пожалуйста, используйте /start для регистрации.")
        return

    settings_text = (
        f"<b>Ваши текущие настройки:</b>\n\n"
    )

    keyboard = await get_settings_keyboard()

    await message.answer(settings_text, reply_markup=keyboard)
    logger.info(f"User (ID: {user_id}) requested settings.")

@router.callback_query(F.data == 'change_language')
async def change_language(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для изменения языка пользователя.
    """
    await state.set_state(FSMSettings.waiting_for_language)
    cur_lang = (await Database.get_user_settings(user_id=callback.from_user.id))['language']
    if cur_lang == 'ru':
        await Database.set_user_setting(user_id=callback.from_user.id, setting='language', value='en')
        new_lang = 'en'
    elif cur_lang == 'en':
        await Database.set_user_setting(user_id=callback.from_user.id, setting='language', value='ru')
        new_lang = 'ru'

    await callback.answer(text=f"Язык изменен на {new_lang.upper()}.")


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отмены текущего действия.
    """
    await state.clear()
    await callback.message.delete()

    await callback.message.answer("Действие отменено.", reply_markup=await get_menu_keyboard())

    logger.info(f"User (ID: {callback.from_user.id}) canceled the action.")

    await callback.answer()

@router.callback_query(F.data.startswith("choice_"), StateFilter(FSMModel.choosing_model))
async def callback_choose_model(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора модели для чата.
    """
    model = callback.data.split("_")[-1]

    if model == "gpt4o":
        await callback.message.edit_text("Модель GPT4o. Это крутая и дорогая модель!\nВы уверены, что хотите её выбрать?",
                                         reply_markup=await get_approve_gpt4o_keyboard())
    elif model == "scenary":
        await callback.message.edit_text("Режим «сценарный». Поможет ответить на вопросы про МИСИС! Вы уверены, что хотите её выбрать?\n(пс, это писал даня, оно того не стоит брат)",
                                         reply_markup=await get_approve_scenary_keyboard())

@router.callback_query(F.data.startswith("approve"), StateFilter(FSMModel.choosing_model))
async def callback_approve_model(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора модели для чата.
    """
    model = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    success = await Database.set_user_setting(user_id=user_id, setting="chat_model", value=model)
    if success:
        if model == "gpt4o":
            await callback.message.edit_text("Модель GPT4o успешно выбрана.")
        elif model == "scenary":
            await callback.message.edit_text("Режим «сценарный» успешно выбран.")

        logger.info(f"User (ID: {user_id}) changed chat model to {model}.")
    else:
        await callback.message.edit_text("Не удалось изменить модель. Попробуйте позже.")
        logger.error(f"Failed to change chat model for user (ID: {user_id}).")

    await state.clear()
    await callback.answer()

@router.message(Command("chat"))
@router.message(F.text == "🗨️ Запустить чат")
async def cmd_chat(message: Message, state: FSMContext):
    """
    Обработчик сообщения "🗨️ Запустить чат".
    Переводит пользователя в состояние ожидания сообщения для ChatGPT.
    """

    model = await Database.get_user_model(user_id=message.from_user.id)

    full_model = "GPT4o" if model == "gpt4o" else "Сценарный"

    if model == "gpt4o":
        await state.set_state(FSMModel.waiting_for_message_gpt4o)
    elif model == "scenary":
        await state.set_state(FSMModel.waiting_for_message_scenary)

    await message.answer(f"Вы сейчас используете: {full_model}\n\nВведите ваше сообщение:", reply_markup=await get_cancel_keyboard())


    logger.info(f"User (ID: {message.from_user.id}) is starting a chat with ChatGPT.")

@router.message(StateFilter(FSMModel.waiting_for_message_gpt4o))
async def process_gpt4o_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с ChatGPT.
    """
    user_message = message.text
    user_id = message.from_user.id

    await state.set_state(FSMModel.gpt4o_processing_message)
    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с ChatGPT API
    # Пример:
    # gpt_response = await get_gpt_response(user_message)
    gpt_response = "This is a sample response from ChatGPT."

    await message.answer(gpt_response)
    logger.info(f"Response sent to user (ID: {user_id}): {gpt_response}")

    await state.clear()

@router.message(StateFilter(FSMModel.waiting_for_message_scenary))
async def process_scenary_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с ChatGPT.
    """
    user_message = message.text
    user_id = message.from_user.id

    await state.set_state(FSMModel.scenary_processing_message)
    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с ChatGPT API
    # Пример:
    # gpt_response = await get_gpt_response(user_message)
    scenary_response = "This is a sample response from Scenary."

    await message.answer(scenary_response)
    logger.info(f"Response sent to user (ID: {user_id}): {scenary_response}")

    await state.clear()

@router.message(StateFilter(FSMModel.scenary_processing_message))
async def fallback_handler(message: Message, state: FSMContext):
    """
    Обработчик для непредвиденных состояний.
    """
    await message.answer("Я не знаю, как на это отвечать :(")
    logger.error(f"Unexpected state while processing a message from user (ID: {message.from_user.id}).")
    await state.clear()
