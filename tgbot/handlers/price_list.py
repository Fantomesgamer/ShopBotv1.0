from aiogram import Router, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.filters.role import IsOperator
from tgbot.handlers.set_message import update_data

router = Router()

"""
Message Handlers
"""

@router.message(F.text.startswith('#PriceList'), IsOperator())
async def on_price_list(message: Message, state: FSMContext, db_session):
    answer = '<b>Прайс лист изменён</b>\n\n'
    await update_data('price_list', message.text.lstrip('#PriceList'))
    await message.answer(answer)
