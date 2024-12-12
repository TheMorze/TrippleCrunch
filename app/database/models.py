from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей базы данных."""
    pass


class UserData(Base):
    """
    Модель для хранения данных пользователя, необходимых для работы бота с интеграцией ChatGPT.
    """
    __tablename__ = 'user_data'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    fullname: Mapped[str] = mapped_column(String(250), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    language: Mapped[str] = mapped_column(String(10), default='ru')  # Настройка языка пользователя
    chat_model: Mapped[str] = mapped_column(String(20), default="gpt4o")  # Настройка модели ChatGPT
    token_balance: Mapped[int] = mapped_column(Integer, default=0)  # Баланс токенов

    gpt4o_access: Mapped[bool] = mapped_column(Boolean, default=True)  # Доступ к GPT4o
    scenary_access: Mapped[bool] = mapped_column(Boolean, default=True) # Доступ к сценарному
    banned: Mapped[bool] = mapped_column(Boolean, default=False)  # Забанен ли пользователь

    # Дополнительные поля для интеграции с ChatGPT
    conversation_history: Mapped[str] = mapped_column(String, default='')  # История разговоров пользователя
    last_interaction: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Время последнего взаимодействия

    def __repr__(self):
        return (f'UserData(user_id={self.user_id!r}, username={self.username!r}, '
                f'fullname={self.fullname!r}, language={self.language!r})')
