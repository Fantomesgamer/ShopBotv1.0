from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateProductStates(StatesGroup):
    article = State()
    ratings = State()
