import asyncio
import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from loguru import logger

from app.database.requests import Database
from app.FSM.fsm import FSMSettings, FSMModel, FSMAdmin
from aiogram.fsm.state import default_state
from app.keyboards.inline_keyboards import (
    get_settings_keyboard,
    get_hide_keyboard,
    get_choose_model_keyboard,
    get_approve_gpt4o_keyboard,
    get_approve_scenary_keyboard,
    get_admin_keyboard,
    get_admin_user_editing_keyboard,
    get_user_model_access_keyboard
)

from app.keyboards.reply_keyboards import (
    get_menu_keyboard
)

from app.service.helpers import get_gpt_response

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from app.lexicon.bot_lexicon import LEXICON_RU, LEXICON_EN

router = Router()

@router.callback_query(F.data == "enter_admin_panel")
async def callback_enter_admin_panel(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Войти в админ-панель".
    """

    settings = await Database.get_user_settings(callback.from_user.id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    if cur_lang == 'ru':
        await callback.message.edit_text("Вы вошли в админ-панель.")
        await callback.message.answer(text="Меню администратора", reply_markup=await get_admin_keyboard(lang='ru'))
    else:
        await callback.message.edit_text("You have entered the admin panel.")
        await callback.message.answer(text="Admin menu", reply_markup=await get_admin_keyboard(lang='en'))

    await state.set_state(FSMAdmin.entered_admin_panel)
    await callback.answer()

@router.callback_query(F.data == "find_user", StateFilter(FSMAdmin.entered_admin_panel))
async def callback_find_user(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Поиск пользователей".
    """
    settings = await Database.get_user_settings(callback.from_user.id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    await state.set_state(FSMAdmin.searching_for_user)

    if cur_lang == 'ru':
        await callback.message.edit_text("Поиск пользователя")
        await callback.message.answer("Введите ID пользователя:")
    else:
        await callback.message.edit_text("User search")
        await callback.message.answer("Enter user ID:")

    await callback.answer()

@router.message(F.text.isdigit(), StateFilter(FSMAdmin.searching_for_user))
async def process_user_search(message: Message, state: FSMContext):
    """
    Обработчик ввода ID пользователя для поиска.
    """
    user_id = int(message.text.strip())

    user_settings = await Database.get_user_settings(user_id)
    user_data = await Database.get_user(user_id)

    settings = await Database.get_user_settings(message.from_user.id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    if user_settings:
        if cur_lang == 'ru':
            await message.answer(f"Пользователь найден: {user_data.fullname}\n\n" \
                                 f"Язык пользователя: {user_data.language}\n" \
                                 f"Выбранная модель: {user_data.chat_model}\n" \
                                 f"Баланс токенов: {user_data.token_balance}\n\n" \
                                 f"Пользователь весь ваш. Что прикажете с ним сделать? 😏",
                                 reply_markup=await get_admin_user_editing_keyboard())
        else:
            await message.answer(f"User found: {user_data.fullname}\n\n" \
                                 f"User language: {user_data.language}\n" \
                                 f"Selected model: {user_data.chat_model}\n" \
                                 f"Token balance: {user_data.token_balance}\n\n" \
                                 f"What do you want to do with this user? 😏",
                                 reply_markup=await get_admin_user_editing_keyboard())

        await state.update_data(data={"user": user_data})
        await state.set_state(FSMAdmin.user_editing)

    else:
        if cur_lang == 'ru':
            await message.answer("Пользователь не найден.")
        else:
            await message.answer("User not found.")



@router.callback_query(F.data == "change_user_model", StateFilter(FSMAdmin.user_editing))
async def callback_change_user_model(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик изменения модели чата для пользователя.
    """
    data = (await state.get_data())['user']
    settings = await Database.get_user_settings(data.user_id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    await state.set_state(FSMAdmin.changing_user_model)

    await callback.message.delete()
    if cur_lang == 'ru':
        await callback.message.answer(f"Изменить доступ к модели для пользователя {data.fullname} (@{data.username}):",
                                      reply_markup=await get_user_model_access_keyboard(gpt=data.gpt4o_access,
                                                                                        scenary=data.scenary_access,
                                                                                        llama=data.llama_access,
                                                                                        lang='ru'))
    else:
        await callback.message.answer(f"Choose the chat model for the user {data.fullname} (@{data.username}):",
                                      reply_markup=await get_user_model_access_keyboard(gpt=data.gpt4o_access,
                                                                                        scenary=data.scenary_access,
                                                                                        llama=data.llama_access,
                                                                                        lang='en'))

    await callback.answer()


@router.callback_query(F.data.startswith("access"), StateFilter(FSMAdmin.changing_user_model))
async def callback_access(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик доступа к модели GPT4o для пользователя.
    """
    mdl = callback.data.split('_')[1]
    data = (await state.get_data())['user']
    if mdl == 'gpt4o':
        data.gpt4o_access = edit = not data.gpt4o_access
    elif mdl == 'scenary':
        data.scenary_access = edit = not data.scenary_access
    else:
        data.llama_access = edit = not data.llama_access

    await state.update_data(data={'user': data})
    await Database.set_user_setting(user_id=data.user_id, setting=f"{mdl}_access", value=edit)
    settings = await Database.get_user_settings(data.user_id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    await callback.message.delete()
    if cur_lang == 'ru':
        await callback.message.answer(f"Настройки доступа были изменены успешно для пользователя {data.fullname} (@{data.username}):",
                                      reply_markup=await get_admin_user_editing_keyboard())
    else:
        await callback.message.answer(f"Access settings have been edited successfully for the user {data.fullname} (@{data.username}):",
                                      reply_markup=await get_admin_user_editing_keyboard())

    await state.set_state(FSMAdmin.user_editing)
    await callback.answer()

@router.callback_query(F.data == "change_user_token_balance", StateFilter(FSMAdmin.user_editing))
async def callback_change_user_token_balance(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик изменения баланса токенов для пользователя.
    """
    data = (await state.get_data())['user']
    settings = await Database.get_user_settings(data.user_id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    await state.set_state(FSMAdmin.changing_user_token_balance)

    await callback.message.delete()
    if cur_lang == 'ru':
        await callback.message.answer(f"Текущий баланс токенов пользователя {data.fullname} (@{data.username}): {data.token_balance}\n\n"
                                      f"Введите новое значение:")
    else:
        await callback.message.answer(f"Current token balance for the user {data.fullname} (@{data.username}): {data.token_balance}\n\n"
                                      f"Enter new value:")

    await callback.answer()


@router.message(F.text.isdigit(), StateFilter(FSMAdmin.changing_user_token_balance))
async def process_user_token_balance(message: Message, state: FSMContext):
    """
    Обработчик ввода нового баланса токенов для пользователя.
    """
    new_balance = int(message.text.strip())
    data = (await state.get_data())['user']
    user = await Database.get_user(data.user_id)
    await Database.set_user_setting(user_id=data.user_id, setting="token_balance", value=new_balance)
    settings = await Database.get_user_settings(data.user_id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    await message.delete()
    if cur_lang == 'ru':
        await message.answer(f"Баланс токенов пользователя {data.fullname} (@{data.username}) успешно изменен на {new_balance}.",
                             reply_markup=await get_admin_user_editing_keyboard())
    else:
        await message.answer(f"Token balance for the user {data.fullname} (@{data.username}) has been successfully changed to {new_balance}.",
                             reply_markup=await get_admin_user_editing_keyboard())

    await state.set_state(FSMAdmin.user_editing)
    await state.update_data(data={"user": data})

@router.message(StateFilter(FSMAdmin.changing_user_token_balance))
@router.message(StateFilter(FSMAdmin.searching_for_user))
async def process_user_token_balance_invalid(message: Message, state: FSMContext):
    """
    Обработчик неверного ввода баланса токенов для пользователя.
    """
    settings = await Database.get_user_settings(message.from_user.id)

    if settings:
        cur_lang = settings.get('language', 'ru')

    if cur_lang == 'ru':
        await message.answer("Введите число.")
    else:
        await message.answer("Enter a number.")
