from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message

from tgbot.config import select_operator
from tgbot.filters.role import IsSuperUser
from tgbot.handlers.cancel import cancel_markup

router = Router()
"""
States
"""


class SelectOperatorStates(StatesGroup):
    user_id = State()

"""
Message Handlers
"""


@router.message(IsSuperUser(),F.text == '/select_operator', state='*')
async def on_set_operator(message: Message, state: FSMContext):
    await message.answer('<b>Выбор оператора</b>\n'
                         'Введите Telgram ID оператора, ID всех операторов можно посмотреть командой: /operators\n'
                         '<i>Данный оператор будет получать все обращения, введите 0, если не хотите принимать обращения.</i>',
                         reply_markup=cancel_markup.as_markup())
    await state.set_state(SelectOperatorStates.user_id)


@router.message(F.text.isdigit(), IsSuperUser(), state=SelectOperatorStates.user_id)
async def enter_user_id(message: Message, state: FSMContext):
    select_operator(int(message.text))
    await message.answer('<b>Оператор успешно выбран</b>')
    await state.clear()
