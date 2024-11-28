from aiogram.fsm.state import State, StatesGroup

class FSMSettings(StatesGroup):
    """
    Состояния для управления настройками пользователя.
    """
    waiting_for_language = State()  # Ожидание выбора языка
    waiting_for_theme = State()     # Ожидание выбора темы

class FSMModel(StatesGroup):
    """
    Состояния для взаимодействия с Model.
    """
    choosing_model = State()


    waiting_for_message_gpt4o = State()   # Ожидание сообщения от пользователя (GPT4o)
    waiting_for_message_scenary = State() # Ожидание сообщения от пользователя (Scenary)

    gpt4o_processing_message = State()    # Обработка сообщения
    scenary_processing_message = State()  # Обработка сообщения

    sending_response = State()      # Отправка ответа пользователю
