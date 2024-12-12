from datetime import datetime
from loguru import logger
from typing import Tuple, Dict, Optional, List

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import select, update

from app.database.models import Base, UserData


class Database:
    """Класс для управления базой данных бота."""

    __engine = create_async_engine(
        url='sqlite+aiosqlite:///app/database/database.db',
        echo=True
    )
    __async_session = async_sessionmaker(__engine, expire_on_commit=False)

    @classmethod
    async def create_tables(cls):
        """Создание таблиц в базе данных."""
        async with cls.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables have been successfully created.")

    @classmethod
    async def add_user(cls, user_id: int, username: str, fullname: Optional[str] = "") -> Tuple[Optional[UserData], bool]:
        """
        Добавление нового пользователя или получение существующего.

        :param user_id: Уникальный ID пользователя Telegram.
        :param username: Имя пользователя Telegram.
        :param fullname: Полное имя пользователя.
        :return: Кортеж с объектом пользователя и флагом существования в базе.
        """
        try:
            async with cls.__async_session() as session:
                user = await session.scalar(select(UserData).where(UserData.user_id == user_id))
                if not user:
                    user = UserData(
                        user_id=user_id,
                        username=username,
                        fullname=fullname or username,
                        registration_date=datetime.utcnow()
                    )
                    session.add(user)
                    await session.commit()
                    logger.debug(f"New user added: {username} (ID: {user_id})")
                    return user, False
                logger.debug(f"User already exists: {username} (ID: {user_id})")
                return user, True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return None, False

    @classmethod
    async def get_user(cls, user_id: int) -> Optional[UserData]:
        """
        Получение информации о пользователе по ID.

        :param user_id: Уникальный ID пользователя Telegram.
        :return: Объект пользователя или None, если не найден.
        """
        try:
            async with cls.__async_session() as session:
                user = await session.scalar(select(UserData).where(UserData.user_id == user_id))
                if user:
                    logger.debug(f"User information retrieved: {user.username} (ID: {user_id})")
                else:
                    logger.debug(f"User with ID {user_id} not found.")
                return user
        except Exception as e:
            logger.error(f"Error retrieving user: {e}")
            return None

    @classmethod
    async def update_user_data(cls, user_id: int, **kwargs) -> bool:
        """
        Обновление данных пользователя.

        :param user_id: Уникальный ID пользователя Telegram.
        :param kwargs: Поля для обновления.
        :return: True, если обновление прошло успешно, иначе False.
        """
        try:
            async with cls.__async_session() as session:
                stmt = (
                    update(UserData)
                    .where(UserData.user_id == user_id)
                    .values(**kwargs)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(stmt)
                await session.commit()
                if result.rowcount:
                    logger.debug(f"User data (ID: {user_id}) updated: {kwargs}")
                    return True
                logger.debug(f"Failed to update user data (ID: {user_id}).")
                return False
        except Exception as e:
            logger.error(f"Error updating user data: {e}")
            return False

    @classmethod
    async def get_all_users(cls) -> List[UserData]:
        """
        Получение списка всех пользователей.

        :return: Список объектов пользователей.
        """
        try:
            async with cls.__async_session() as session:
                users = await session.scalars(select(UserData))
                user_list = users.all()
                logger.debug(f"List of all users retrieved. Count: {len(user_list)}")
                return user_list
        except Exception as e:
            logger.error(f"Error retrieving list of users: {e}")
            return []

    @classmethod
    async def delete_user(cls, user_id: int) -> bool:
        """
        Удаление пользователя из базы данных.

        :param user_id: Уникальный ID пользователя Telegram.
        :return: True, если удаление прошло успешно, иначе False.
        """
        try:
            async with cls.__async_session() as session:
                user = await session.get(UserData, user_id)
                if user:
                    await session.delete(user)
                    await session.commit()
                    logger.debug(f"User (ID: {user_id}) deleted from the database.")
                    return True
                logger.debug(f"User (ID: {user_id}) not found for deletion.")
                return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    @classmethod
    async def get_user_settings(cls, user_id: int) -> Optional[Dict[str, any]]:
        """
        Получение настроек пользователя.

        :param user_id: Уникальный ID пользователя Telegram.
        :return: Словарь с настройками пользователя или None, если пользователь не найден.
        """
        try:
            user = await cls.get_user(user_id)
            if user:
                settings = {
                    "language": user.language,
                    "chat_model": user.chat_model,
                    "gpt4o_access": user.gpt4o_access,
                    "scenary_access": user.scenary_access,
                    "llama_access": user.llama_access,
                    "token_balance": user.token_balance,
                    "banned": user.banned
                }
                logger.debug(f"User settings retrieved (ID: {user_id}): {settings}")
                return settings
            logger.debug(f"Failed to retrieve settings for user (ID: {user_id}).")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user settings: {e}")
            return None

    @classmethod
    async def set_user_setting(cls, user_id: int, setting: str, value: any) -> bool:
        """
        Установка конкретной настройки пользователя.

        :param user_id: Уникальный ID пользователя Telegram.
        :param setting: Название настройки.
        :param value: Значение настройки.
        :return: True, если настройка установлена успешно, иначе False.
        """
        allowed_settings = {"language", "chat_model", "gpt4o_access", "scenary_access", "llama_access", "token_balance", "banned"}
        if setting not in allowed_settings:
            logger.warning(f"Attempted to set unknown setting: {setting}")
            return False
        return await cls.update_user_data(user_id, **{setting: value})


    @classmethod
    async def get_user_model(cls, user_id: int) -> Optional[str]:
        """
        Получение выбранной модели чата для пользователя.

        :param user_id: Уникальный ID пользователя Telegram.
        :return: Название выбранной модели чата или None, если пользователь не найден.
        """
        try:
            user = await cls.get_user(user_id)
            if user:
                logger.debug(f"User model retrieved (ID: {user_id}): {user.chat_model}")
                return user.chat_model
            logger.debug(f"Failed to retrieve user model (ID: {user_id}).")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user model: {e}")
            return None
