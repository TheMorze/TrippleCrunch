from aiogram.fsm.state import State, StatesGroup

class FSMSettings(StatesGroup):
    """
    Состояния для управления настройками пользователя.
    """
    waiting_for_language = State()  # Ожидание выбора языка
    waiting_for_theme = State()     # Ожидание выбора темы

class FSMChatGPT(StatesGroup):
    """
    Состояния для взаимодействия с ChatGPT.
    """
    choosing_model = State()
    waiting_for_message = State()   # Ожидание сообщения от пользователя
    processing_message = State()    # Обработка сообщения
    sending_response = State()      # Отправка ответа пользователю
