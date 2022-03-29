import json

from aiogram import Router, types, F
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.filters.role import IsSuperUser
from tgbot.handlers.cancel import cancel_markup, cancel_button

router = Router()
"""
States
"""


class SetMessages(StatesGroup):
    choice_title = State()
    enter_text = State()


"""
CallbackData
"""


class ChoiceTitle(CallbackData, prefix='set_message'):
    message_title: str


"""
Keyboards
"""
messages_markup = InlineKeyboardBuilder([
    [InlineKeyboardButton(text='Старт', callback_data=ChoiceTitle(message_title='start').pack()),
     InlineKeyboardButton(text='Как сделать заказ?', callback_data=ChoiceTitle(message_title='instruction').pack()),
     InlineKeyboardButton(text='Cвязаться с оператором', callback_data=ChoiceTitle(message_title='questions').pack())
     ],
    [InlineKeyboardButton(text='Сколько длится доставка?', callback_data=ChoiceTitle(message_title='delivery_time').pack()),
     InlineKeyboardButton(text='Как я могу оплатить заказ?', callback_data=ChoiceTitle(message_title='payments').pack()),
    InlineKeyboardButton(text='Как получит трек на посылку?', callback_data=ChoiceTitle(message_title='delivery_track').pack())],

    [InlineKeyboardButton(text='Оформить заказ', callback_data=ChoiceTitle(message_title='buy_product').pack()),
     InlineKeyboardButton(text='Подтвердить оплату заказа', callback_data=ChoiceTitle(message_title='check_payed').pack()),
     InlineKeyboardButton(text='Cотрудничество', callback_data=ChoiceTitle(message_title='cooperation').pack())],

    [InlineKeyboardButton(text='Сайт', callback_data=ChoiceTitle(message_title='website').pack()),
     InlineKeyboardButton(text='Канал', callback_data=ChoiceTitle(message_title='channel').pack()),
     InlineKeyboardButton(text='Беседа', callback_data=ChoiceTitle(message_title='group').pack())],
    [cancel_button]
]).as_markup()
"""
Message Handlers
"""


@router.message(IsSuperUser(), F.text == '/set_message')
async def on_set_message(message: Message, state: FSMContext):
    await message.answer('<b>Какой текст вы хотите изменить?</b>', reply_markup=messages_markup)
    await state.set_state(SetMessages.choice_title)


@router.callback_query(state=SetMessages.choice_title)
async def choice_title(query: CallbackQuery, state: FSMContext):

    message_title = query.data[12::]
    await state.update_data(message_title=message_title)

    await query.message.answer('<b>Пришлите новый текст</b>', reply_markup=cancel_markup)
    await state.set_state(SetMessages.enter_text)


@router.message(state=SetMessages.enter_text)
async def enter_text(message: Message, state: FSMContext):
    message_title = (await state.get_data()).get('message_title')
    await update_data(message_title, message.text)
    await message.answer('<b>Успешно изменено</b>')
    await state.clear()


"""
Misc
"""


async def get_message(message_title: str) -> str:
    data = await get_data()
    return data['messages'].get(message_title) or message_title


async def get_data() -> dict:
    with open("messages.json", "r") as read_file:
        data = json.load(read_file)
        return data


async def update_data(message_title: str, message_text: str):
    old_data = await get_data()
    old_data['messages'][message_title] = message_text
    with open("messages.json", "w") as write_file:
        json.dump(old_data, write_file)
