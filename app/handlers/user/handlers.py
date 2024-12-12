import asyncio
import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from loguru import logger

from app.database.requests import Database
from app.FSM.fsm import FSMSettings, FSMModel, FSMUser
from aiogram.fsm.state import default_state
from app.keyboards.inline_keyboards import (
    get_settings_keyboard,
    get_hide_keyboard,
    get_choose_model_keyboard,
    get_approve_gpt4o_keyboard,
    get_approve_llama3_keyboard,
    get_approve_scenary_keyboard,
    get_approve_keyboard
)

from app.keyboards.reply_keyboards import (
    get_menu_keyboard
)

from app.service.helpers import get_gpt_response, get_llama_response, get_scenary_response

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from app.lexicon.bot_lexicon import LEXICON_RU, LEXICON_EN

from aiogram.types import FSInputFile

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Регистрирует пользователя в базе данных и приветствует его.
    """
    user_id = message.from_user.id
    username = message.from_user.username or ""
    fullname = message.from_user.full_name or ""

    user, created = await Database.add_user(user_id=user_id, username=username, fullname=fullname)

    settings = await Database.get_user_settings(user_id)

    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    if not created:
        await state.set_state(FSMUser.approving_agreement)
        welcome_text_ru = f"Добро пожаловать, <b>{fullname}</b>!\n\n" \
                          f"Перед использованием бота вам следует ознакомиться с политикой конфиденциальности и подтвердить принятие пользовательского соглашения ☝️"
        welcome_text_en = f"Welcome, <b>{fullname}</b>!\n\n" \
                          f"Before using the bot, please familiarize yourself with the privacy policy and accept the user agreement ☝️"

        # Путь к локальному PDF-файлу
        pdf_path = "app\database\Пользовательское соглашение.pdf"

        ## Используем FSInputFile для отправки локального файла
        pdf_file = FSInputFile(pdf_path)

        await message.answer_document(pdf_file, caption="Пользовательское соглашние 📄")
        if cur_lang == 'ru':
            await message.answer(text=welcome_text_ru, reply_markup=await get_approve_keyboard())
        else:
            await message.answer(text=welcome_text_en, reply_markup=await get_approve_keyboard())

        return

    else:
        welcome_text_ru = f"С возвращением, <b>{fullname}</b>!"
        welcome_text_en = f"Welcome, <b>{fullname}</b>!"

    if cur_lang == 'ru':
        await message.answer(LEXICON_RU['start'].format(hello=welcome_text_ru), reply_markup=await get_menu_keyboard(lang='ru'))
    else:
        await message.answer(LEXICON_EN['start'].format(hello=welcome_text_en), reply_markup=await get_menu_keyboard(lang='en'))

    logger.info(f"User {username} (ID: {user_id}) started the bot.")


@router.callback_query(F.data == 'approve', StateFilter(FSMUser.approving_agreement))
async def callback_approve(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик согласия пользователя с политикой конфиденциальности.
    """
    user_id = callback.from_user.id
    username = callback.from_user.username or ""
    fullname = callback.from_user.full_name or ""

    settings = await Database.get_user_settings(user_id)

    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    await state.set_state(default_state)

    welcome_text_ru = f"С возвращением, <b>{fullname}</b>!"
    welcome_text_en = f"Welcome, <b>{fullname}</b>!"

    await callback.message.delete()
    if cur_lang == 'ru':
        await callback.message.answer(LEXICON_RU['start'].format(hello=welcome_text_ru), reply_markup=await get_menu_keyboard(lang='ru'))
    else:
        await callback.message.answer(LEXICON_EN['start'].format(hello=welcome_text_en), reply_markup=await get_menu_keyboard(lang='en'))

    await callback.answer()

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

    settings = await Database.get_user_settings(user_id=user_id)
    gpt4o = settings['gpt4o_access']
    scenary = settings['scenary_access']
    llama = settings['llama_access']

    if cur_lang == 'ru':
        text = "Выберите модель для чата.\n\nВам доступны следующие модели:"
    else:
        text = "Choose a chat model.\n\nYou have access to the folowing models:"

    await message.answer(text, reply_markup=await get_choose_model_keyboard(gpt4o=gpt4o, scenary=scenary, llama=llama, lang=cur_lang))
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

    is_admin = (await Database.get_user(user_id=user_id)).is_admin

    keyboard = await get_settings_keyboard(lang=cur_lang, is_admin=is_admin)

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
    is_admin = (await Database.get_user(user_id=user_id)).is_admin

    if cur_lang == 'ru':
        await Database.set_user_setting(user_id=user_id, setting='language', value='en')
        new_lang = 'en'
        response_text = "Language changed to EN."
        await callback.message.answer("<b>Your current settings:</b>\n\n", reply_markup=await get_settings_keyboard(lang='en', is_admin=is_admin))
        await callback.message.answer("Settings have been changed", reply_markup=await get_menu_keyboard(lang='en'))
    else:
        await Database.set_user_setting(user_id=user_id, setting='language', value='ru')
        new_lang = 'ru'
        response_text = "Язык изменен на RU."
        await callback.message.answer("<b>Ваши текущие настройки:</b>\n\n", reply_markup=await get_settings_keyboard(lang='ru', is_admin=is_admin))
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

    if state.get_state() not in (FSMModel.waiting_for_message_gpt4o, FSMModel.waiting_for_message_llama3, FSMModel.waiting_for_message_scenary):
        await state.clear()

    await callback.message.delete()

    logger.info(f"User (ID: {user_id}) hided the action.")

    await callback.answer()

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Обработчик команды "/cancel".
    Отменяет текущее действие пользователя.
    """
    cur_lang = (await Database.get_user_settings(user_id=message.from_user.id))['language']
    await state.clear()

    await message.answer("Действие отменено" if cur_lang == 'ru' else "Action cancelled", reply_markup=await get_menu_keyboard(lang=cur_lang))


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
    elif model == "llama3":
        if cur_lang == 'ru':
            text = LEXICON_RU['llama3_choice']
        else:
            text = LEXICON_EN['llama3_choice']
        keyboard = await get_approve_llama3_keyboard(lang=cur_lang)
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
        elif model == "llama3":
            if cur_lang == 'ru':
                text = "Модель Llama3 успешно выбрана."
            else:
                text = "Llama3 model has been successfully selected."
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
    token_balance = settings['token_balance']

    if model == "gpt4o":
        if token_balance < 100:
            if cur_lang == 'ru':
                await message.answer(f"У вас недостаточно токенов для использования модели GPT4o.\n\n<b>Пополните баланс токенов, чтобы продолжить — для этого напишите @TheMorz3.</b>" \
                                f"\n\n <i>/price — узнать прайс-лист</i>")
            else:
                await message.answer(f"You don't have enough tokens to use model GPT4o. Please top up your token balance to continue. DM @TheMorze in order to do it.")
            return
        full_model = "GPT4o"
        await state.set_state(FSMModel.waiting_for_message_gpt4o)
    elif model == "llama3":
        if token_balance < 150:
            if cur_lang == 'ru':
                await message.answer(f"У вас недостаточно токенов для использования модели LLama3.\n\n<b>Пополните баланс токенов, чтобы продолжить — для этого напишите @TheMorz3.</b>" \
                                f"\n\n <i>/price — узнать прайс-лист</i>")
            else:
                await message.answer(f"You don't have enough tokens to use model LLama3. Please top up your token balance to continue. DM @TheMorze in order to do it.")
            return
        full_model = "Llama3"
        await state.set_state(FSMModel.waiting_for_message_llama3)
    elif model == "scenary":
        if token_balance < 150:
            if cur_lang == 'ru':
                await message.answer(f"У вас недостаточно токенов для использования модели LLama3.\n\n<b>Пополните баланс токенов, чтобы продолжить — для этого напишите @TheMorz3.</b>" \
                                f"\n\n <i>/price — узнать прайс-лист</i>")
            else:
                await message.answer(f"You don't have enough tokens to use model LLama3. Please top up your token balance to continue. DM @TheMorze in order to do it.")
            return
        full_model = "Scenary"
        await state.set_state(FSMModel.waiting_for_message_scenary)
    else:
        # Default model
        full_model = "GPT4o"
        await state.set_state(FSMModel.waiting_for_message_gpt4o)

    if cur_lang == 'ru':
        prompt = f"Вы сейчас используете: {full_model}\n\nВведите ваше сообщение:\n\n<i>Чтобы отменить диалог, нажмите /cancel</i>"
    else:
        prompt = f"You are now using: {full_model}\n\nEnter your message:\n\n<i>In order to quit the dialogue, click /cancel</i>"

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


    token_balance = settings['token_balance']

    if token_balance < 100:
        if cur_lang == 'ru':
            await message.answer(f"У вас недостаточно токенов для использования модели GPT4o.\n\n<b>Пополните баланс токенов, чтобы продолжить — для этого напишите @TheMorz3.</b>" \
                                f"\n\n <i>/price — узнать прайс-лист</i>")
        else:
            await message.answer(f"You don't have enough tokens to use model GPT4o. Please top up your token balance to continue. DM @TheMorze in order to do it.")
        return

    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')

    gpt_response = await get_gpt_response(user_message)

    await Database.set_user_setting(user_id=user_id, setting="token_balance", value=(await Database.get_user_settings(user_id=user_id))['token_balance'] - 100)

    await message.answer(gpt_response)
    logger.info(f"Response sent to user (ID: {user_id}): {gpt_response}")


@router.message(StateFilter(FSMModel.waiting_for_message_llama3))
async def process_llama3_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с Llama3.
    """
    user_message = message.text
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    token_balance = settings['token_balance']
    if token_balance < 150:
        if cur_lang == 'ru':
            await message.answer(f"У вас недостаточно токенов для использования модели LLama3.\n\n<b>Пополните баланс токенов, чтобы продолжить — для этого напишите @TheMorz3.</b>" \
                                f"\n\n <i>/price — узнать прайс-лист</i>")
        else:
            await message.answer(f"You don't have enough tokens to use model LLama3. Please top up your token balance to continue. DM @TheMorze in order to do it.")
        return

    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с Llama API
    # Пример:
    # llama_response = await get_llama_response(user_message)
    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')

    llama_response = await get_llama_response(user_message)

    await Database.set_user_setting(user_id=user_id, setting="token_balance", value=(await Database.get_user_settings(user_id=user_id))['token_balance'] - 150)
    await message.answer(llama_response)
    logger.info(f"Response sent to user (ID: {user_id}): {llama_response}")
    
@router.message(StateFilter(FSMModel.waiting_for_message_scenary))
async def process_scenary_message(message: Message, state: FSMContext):
    """
    Обработчик сообщений в состоянии общения с Scenary.
    """
    user_message = message.text
    user_id = message.from_user.id
    settings = await Database.get_user_settings(user_id=user_id)
    if settings:
        cur_lang = settings.get('language', 'ru')
    else:
        cur_lang = 'ru'  # Default language

    token_balance = settings['token_balance']
    if token_balance < 50:
        if cur_lang == 'ru':
            await message.answer(f"У вас недостаточно токенов для использования модели Scenary.\n\n<b>Пополните баланс токенов, чтобы продолжить — для этого напишите @TheMorz3.</b>"
                                 f"\n\n <i>/price — узнать прайс-лист</i>")
        else:
            await message.answer(f"You don't have enough tokens to use model Scenary. Please top up your token balance to continue. DM @TheMorze in order to do it.")
        return

    logger.info(f"Message received from user (ID: {user_id}): {user_message}")

    # Здесь можно добавить интеграцию с Llama API
    # Пример:
    # llama_response = await get_llama_response(user_message)
    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')

    scenary_response = await get_scenary_response(user_message)

    await Database.set_user_setting(user_id=user_id, setting="token_balance", value=(await Database.get_user_settings(user_id=user_id))['token_balance'] - 50)
    await message.answer(scenary_response)
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

@router.message(F.text == '🆘 Помощь')
@router.message(F.text == '🆘 Help')
async def cmd_help(message: Message):
    """
    Обработчик команды "🆘 Помощь" и команды "/help".
    Отправляет сообщение с помощью.
    """

    await message.answer("<b><i>==ПОМОЩЬ==</i></b>\n\n" \
                         "🗨 <b><i>Запустить чат</i></b> — <i>Начать общение с выбранной моделью нейросети</i>\n" \
                         "🤖 <b><i>Изменить модель</i></b> — <i>выбрать модель из существующих</i>\n" \
                         "⚙️ <b><i>Настройки</i></b> — <i>Изменить язык</i> или <i>Войти в админ-панель (при наличии прав)</i>\n" \
                         "📚 <b><i>О нас</i></b> — информация о команде разработчиков\n" \
                         "📜 <b><i>Прайс-лист</i></b> — актуальные цены на токены")


@router.message(F.text == '📚 О нас')
@router.message(F.text == '📚 About us')
async def about_us(message: Message):
    """
    Обработчик команды "📚 О нас" и команды "/about".
    Отправляет сообщение с информацией о боте.
    """
    await message.answer("<b><i>==О НАС==</i></b>\n\nМы команда из трех молодых энтузиастов,"
                        "решивших собрать все самое нужное "
                        "для студента / абитуриента МИСИС в одном боте.\n\n"
                        "Предложения по улучшению работы сервиса принимаются"
                        "только от Павла Дмитриевича, напишите нам в лс - бан ☠️")

@router.message(F.text == '📜 Прайс-лист')
@router.message(F.text == '📜 Price List')
@router.message(Command('price'))
async def price_list(message: Message):
    """
    Обработчик команды "Прайс-лист" и команды "/pricelist".
    Отправляет сообщение с прайс-листом.
    """
    cur_lang = (await Database.get_user_settings(message.from_user.id))['language']

    if cur_lang == 'ru':
        await message.answer('''<b>🌟 Прайс-лист на услуги чат-бота 🌟\n\n\n</b>🔹 10 тыс. токенов — 50 рублей\n
🔹 100 тыс. токенов — 300 рублей\n
🔹 1 млн. токенов — 2500 рублей\n''')

    else:
        await message.answer('''<b>🌟 Chat bot service price list 🌟\n\n</b>

🔹 10,000 tokens — 50 rubles\n

🔹 100,000 tokens — 300 rubles\n

🔹 1,000,000 tokens — 2500 rubles\n''')




























































@router.message(F.text.lower().contains('хонер'))
async def process_some(message: Message):
    """
    Обработчик сообщений, содержащих 'хонер'.
    Отправляет сообщение с приветствием.
    """
    await message.answer("<b><i>==ХУАВЕЙ==  :)</i></b>")
