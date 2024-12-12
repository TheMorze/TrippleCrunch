from aiogram.fsm.state import State, StatesGroup

class FSMUser(StatesGroup):
    """
    Состояния для управления пользователями.
    """
    approving_agreement = State()  # Ожидание согласия на пользовательское соглашение

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
    waiting_for_message_llama3 = State()  # Ожидание сообщения от пользователя (Llama3)
    waiting_for_message_scenary = State() # Ожидание сообщения от пользователя (Scenary)

    gpt4o_processing_message = State()    # Обработка сообщения
    scenary_processing_message = State()  # Обработка сообщения

    sending_response = State()      # Отправка ответа пользователю

class FSMAdmin(StatesGroup):
    """
    Состояния для взаимодействия с админ-панелью.
    """
    entered_admin_panel = State()  # Вход в админ-панель
    searching_for_user = State()      # Поиск пользователей
    user_editing = State()            # Редактирование пользователя
    changing_user_model = State()
    changing_user_token_balance = State()