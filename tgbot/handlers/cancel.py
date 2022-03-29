from aiogram import Router, F
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

"""
CallbackData
"""


class Cancel(CallbackData, prefix='cancel'):
    pass


"""
Keyboards
"""

cancel_button = InlineKeyboardButton(text='Отмена', callback_data=Cancel().pack())
cancel_markup = InlineKeyboardBuilder([[cancel_button]])

"""
Message Handlers
"""


@router.message(F.text == '/cancel')
async def on_cancel(message: Message, state: FSMContext):
    await message.answer('<b>Отменено</b>')
    await state.clear()


"""
CallbackQuery handlers
"""


@router.callback_query(Cancel.filter())
async def on_cancel(query: CallbackQuery, state: FSMContext):
    await query.answer('Отменено')
    await state.clear()
