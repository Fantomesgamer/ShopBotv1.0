from aiogram import Router, types, F
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from enum import Enum

from tgbot.config import load_config

config = load_config('bot.ini').tg_bot
router = Router()

"""
Misc
"""


class MenuActions(str, Enum):
    questions = 'QUESTIONS'
    shop = 'SHOP'
    delivery = 'DELIVERY'


"""
CallbackData
"""


class MenuChoice(CallbackData, prefix='menu_choice'):
    action: MenuActions


"""
Keyboards
"""


async def gen_menu_markup(*args, **kwargs) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Товары', callback_data=MenuChoice(action=MenuActions.shop).pack()))
    builder.row(InlineKeyboardButton(text='Где моя посылка?', callback_data=MenuChoice(action=MenuActions.delivery).pack()))
    builder.row(InlineKeyboardButton(text='Другие вопросы', callback_data=MenuChoice(action=MenuActions.questions).pack()))
    builder.row(InlineKeyboardButton(text='Сайт', url=config.website),
                InlineKeyboardButton(text='Канал', url=config.channel),
                InlineKeyboardButton(text='Беседа', url=config.group))
    return builder.as_markup()


"""
Message Handlers
"""
@router.message(F.text=='/menu')
async def on_menu(message: Message, state: FSMContext):
    await message.answer('<b>Меню</b>', reply_markup=await gen_menu_markup())
    pass
"""
CallbackQuery handlers
"""


@router.callback_query(MenuChoice.filter(F.action == MenuActions.questions), state='*')
async def on_questions(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    text = '<b>Ответы на часто задаваемые вопросы</b>' \
           '' \
           ''
    await query.message.answer(text)

@router.callback_query(MenuChoice.filter(F.action == MenuActions.delivery), state='*')
async def on_delivery(query: CallbackQuery, state: FSMContext, callback_data: MenuActions):
    text = '<b>Где моя посылка?</b>' \
           '' \
           ''
    await query.message.answer(text)
