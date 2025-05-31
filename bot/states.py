from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State


class MenuStates(StatesGroup):
    select_study_program = State()
    main_menu = State()


class AdminStates(StatesGroup):
    admin_menu = State()

    add_study_program = State()
    edit_study_program_name = State()

    add_group = State()
    edit_group_name = State()

    add_option = State()
    edit_option_name = State()
    edit_option_channel = State()

    add_deadline = State()
    edit_deadline_name = State()
    edit_deadline_date = State()


# filter to check if user in admin panel
admin_states_filter = StateFilter(*[state for state in AdminStates.__all_states__])
