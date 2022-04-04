import dataclasses
from enum import Enum
from random import choice

import loguru
from aiogram import Router, F, Bot
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.config import load_config, get_selected_operator
from tgbot.handlers.cancel import cancel_markup
from tgbot.handlers.select_operator import OperatorTypes
from tgbot.handlers.set_message import get_message
from tgbot.models import User

router = Router()

"""
Misc
"""


@dataclasses.dataclass
class ConnectReason:
    title: str
    message_title: str


class ConnectReasonsNames(str, Enum):
    check_payed = 'CHECK_PAYED'
    buy_product = 'BUY_PRODUCT'
    cooperation = 'COOPERATION'
    questions = 'QUESTIONS'


ConnectReasons = {
    ConnectReasonsNames.check_payed: ConnectReason(title='Проверка оплаты', message_title='check_payed'),
    ConnectReasonsNames.buy_product: ConnectReason(title='Оформление заказа', message_title='buy_product'),
    ConnectReasonsNames.cooperation: ConnectReason(title='Сотрудничество', message_title='cooperation'),
    ConnectReasonsNames.questions: ConnectReason(title='Связаться с оператором', message_title='questions'),
}
"""
States
"""


class ConnectStates(StatesGroup):
    enter_connect_comment = State()


"""
Keyboards
"""


async def gen_user_url_markup(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder([[InlineKeyboardButton(text='Связаться', url=url)]]).as_markup()


"""
CallbackData
"""


class ConnectOperator(CallbackData, prefix='connect_operator'):
    user_id: int
    reason: ConnectReasonsNames


"""
Message Handlers
"""


@router.message(state=ConnectStates.enter_connect_comment)
async def enter_connect_comment(message: Message, state: FSMContext, db_session, bot):
    username = message.from_user.username
    reason: ConnectReason = (await state.get_data()).get('reason')

    if username:
        url = f't.me/{username}'
        operator_id = get_selected_operator(OperatorTypes(reason.message_title))
        if operator_id and operator_id != 0:
            try:
                await bot.send_message(chat_id=operator_id, text='<b>Новое обращеник</b>\n\n'
                                                                      f'<b>Причина:</b>{reason.title}<i></i>\n'
                                                                      f'<b>Комментарий</b>\n'
                                                                      f'{message.text}',
                                       reply_markup=await gen_user_url_markup(url))
            except TelegramBadRequest as e:
                loguru.logger.error(e)
                await message.answer('<b>Не найдено доступных операторов, обратитесь позже</b>\n')
        else:
            await message.answer('<b>Не найдено доступных операторов, обратитесь позже</b>\n')
    else:
        await message.answer('<b>Не заполнен username</b>\n'
                             '<i>Для того чтобы связаться с оператором для оформления заказа, вам необходимо иметь username. \n'
                             'Указать его можно в настройках телеграма.</i>')
    await state.clear()


"""
CallbackQuery handlers
"""


@router.callback_query(ConnectOperator.filter(), state='*')
async def on_connect_operator(query: CallbackQuery, state: FSMContext, callback_data: ConnectOperator, db_session,
                              bot: Bot):
    await state.set_state(ConnectStates.enter_connect_comment)
    reason = ConnectReasons.get(callback_data.reason)

    await state.update_data(reason=reason)
    await query.message.answer(await get_message(reason.message_title),
                               reply_markup=cancel_markup)
