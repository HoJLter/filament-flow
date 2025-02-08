from aiogram.fsm.state import StatesGroup, State


class StatesData(StatesGroup):
    # Стандартное состояние
    none_state = State()
    # Состояния пользователя
    waiting_for_order_name = State()
    waiting_for_references = State()
    waiting_for_index = State()
    waiting_for_file = State()

    # Состояния администратора
    waiting_for_nozzle_temp = State()
    waiting_for_table_temp = State()
    waiting_for_printing_speed = State()
    waiting_for_layer_thickness = State()