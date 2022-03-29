from aiogram import Router, F
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum

from tgbot.config import load_config
from tgbot.handlers.connect_operator import ConnectReasonsNames
from tgbot.handlers.set_message import get_message

config = load_config('bot.ini').tg_bot
router = Router()

"""
Misc
"""


class MenuActions(str, Enum):
    questions = 'QUESTIONS'
    shop = 'SHOP'
    delivery = 'DELIVERY'
    cooperation = 'COOPERATION'
    instruction = 'INSTRUCTION'
    payments = 'PAYMENTS'
    delivery_track = 'DELIVERY_TRACK'


"""
CallbackData
"""


class MenuChoice(CallbackData, prefix='menu_choice'):
    action: MenuActions


"""
Keyboards
"""


async def gen_menu_markup(*args, **kwargs) -> InlineKeyboardMarkup:
    from tgbot.handlers.connect_operator import ConnectOperator
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Прайс лист', callback_data=MenuChoice(action=MenuActions.shop).pack()))
    builder.row(InlineKeyboardButton(text='Как сделать заказ?',
                                     callback_data=MenuChoice(action=MenuActions.instruction).pack()))
    builder.row(
        InlineKeyboardButton(text='Оформить заказ', callback_data=ConnectOperator(user_id=kwargs.get('user').user_id,
                                                                                  reason=ConnectReasonsNames.buy_product).pack()))

    builder.row(InlineKeyboardButton(text='Как получит трек на посылку?',
                                     callback_data=MenuChoice(action=MenuActions.delivery_track).pack()))

    builder.row(InlineKeyboardButton(text='Сколько длится доставка?',
                                     callback_data=MenuChoice(action=MenuActions.delivery).pack()))
    builder.row(InlineKeyboardButton(text='Как я могу оплатить заказ?',
                                     callback_data=MenuChoice(action=MenuActions.payments).pack()))

    builder.row(InlineKeyboardButton(text='Подтвердить оплату заказа',
                                     callback_data=ConnectOperator(user_id=kwargs.get('user').user_id,
                                                                   reason=ConnectReasonsNames.check_payed).pack()))
    builder.row(InlineKeyboardButton(text='Предложения по сотрудничеству',
                                     callback_data=ConnectOperator(user_id=kwargs.get('user').user_id,
                                                                   reason=ConnectReasonsNames.cooperation).pack()))

    builder.row(
        InlineKeyboardButton(text='Связаться с оператором', callback_data=MenuChoice(action=MenuActions.questions).pack()))

    builder.row(InlineKeyboardButton(text='Сайт', url=await get_message('website')),
                    InlineKeyboardButton(text='Канал', url=await get_message('channel')),
                    InlineKeyboardButton(text='Беседа', url=await get_message('group')))

    return builder.as_markup()


"""
Message Handlers
"""


@router.message(F.text == '/start')
@router.message(F.text == '/menu')
async def on_menu(message: Message, state: FSMContext, user):
    await message.answer('<b>Меню</b>', reply_markup=await gen_menu_markup(user=user))
    pass


"""
CallbackQuery handlers
"""


@router.callback_query(MenuChoice.filter(F.action == MenuActions.questions), state='*')
async def on_questions(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    await query.message.answer(await get_message('questions'))


@router.callback_query(MenuChoice.filter(F.action == MenuActions.delivery), state='*')
async def on_delivery(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    await query.message.answer(await get_message('delivery_time'))


@router.callback_query(MenuChoice.filter(F.action == MenuActions.delivery_track), state='*')
async def on_delivery(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    await query.message.answer(await get_message('delivery_track'))


@router.callback_query(MenuChoice.filter(F.action == MenuActions.instruction), state='*')
async def on_instruction(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    await query.message.answer(await get_message('instruction'))


@router.callback_query(MenuChoice.filter(F.action == MenuActions.payments), state='*')
async def on_payments(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    await query.message.answer(await get_message('payments'))


@router.callback_query(MenuChoice.filter(F.action == MenuActions.cooperation), state='*')
async def on_cooperation(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    await query.message.answer(await get_message('cooperation'))


@router.message(F.text == '/shop', state='*')
@router.callback_query(MenuChoice.filter(F.action == MenuActions.shop), state='*')
async def on_shop(query: CallbackQuery):
    message = query
    if type(query) == CallbackQuery:
        message = query.message

    text = await get_message('price_list')
    if text == 'price_list':
        text = '<b>Прайс лист пуст</b>'
    await message.answer(text)
