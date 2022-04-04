from enum import Enum

from aiogram import Router, types, F
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, message
from aiogram.utils.keyboard import InlineKeyboardBuilder


from tgbot.filters.role import IsSuperUser
from tgbot.handlers.cancel import cancel_markup, cancel_button

router = Router()


class OperatorTypes(str, Enum):
    questions = 'questions'
    buy_product = 'buy_product'
    check_payed = 'check_payed'
    cooperation = 'cooperation'


"""
States
"""


class SelectOperatorStates(StatesGroup):
    user_id = State()
    operator_type = State()


"""
CallbackData
"""


class SelectOperatorType(CallbackData, prefix='select_operator_type'):
    operator_type: OperatorTypes


"""
Keyboards
"""
operator_types_markup = InlineKeyboardBuilder([
    [
        InlineKeyboardButton(text='Cвязаться с оператором',
                             callback_data=SelectOperatorType(operator_type=OperatorTypes.questions).pack())
    ],
    [InlineKeyboardButton(text='Оформить заказ',
                          callback_data=SelectOperatorType(operator_type=OperatorTypes.buy_product).pack()),
     InlineKeyboardButton(text='Подтвердить оплату заказа',
                          callback_data=SelectOperatorType(operator_type=OperatorTypes.check_payed).pack()),
     InlineKeyboardButton(text='Cотрудничество',
                          callback_data=SelectOperatorType(operator_type=OperatorTypes.cooperation).pack())],

    [cancel_button]
]).as_markup()

"""
Message Handlers
"""


@router.message(IsSuperUser(), F.text == '/select_operator', state='*')
async def on_set_operator(message: Message, state: FSMContext):
    await message.answer('<b>Выбор оператора</b>\n'
                         'Куда назначить оператора?', reply_markup=operator_types_markup)
    await state.set_state(SelectOperatorStates.operator_type)


@router.message(F.text.isdigit(), IsSuperUser(), state=SelectOperatorStates.user_id)
async def enter_user_id(message: Message, state: FSMContext):
    from tgbot.config import select_operator
    select_operator((await state.get_data()).get('operator_type'), int(message.text))
    await message.answer('<b>Оператор успешно выбран</b>')
    await state.clear()


@router.callback_query(SelectOperatorType.filter(), state=SelectOperatorStates.operator_type)
async def select_operator_type(query: CallbackQuery, state: FSMContext, callback_data: SelectOperatorType):
    await state.update_data(operator_type=callback_data.operator_type)

    await query.message.answer('<b>Выбор оператора</b>\n'
                         'Введите Telgram ID оператора, ID всех операторов можно посмотреть командой: /operators\n'
                         '<i>Данный оператор будет получать все обращения, введите 0, если не хотите принимать обращения.</i>',
                         reply_markup=cancel_markup.as_markup())
    await state.set_state(SelectOperatorStates.user_id)