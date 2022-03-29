from aiogram import Router, F
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.handlers.stages import CreateStagesNames
from tgbot.models import Product

router = Router()

"""
States
"""


class CreateProductStates(StatesGroup):
    name = State()
    price = State()
    category = State()
    complete = State()


"""
CallbackData
"""


class CompleteCreateProduct(CallbackData, prefix='complete_create_product'):
    pass


class GotoStage(CallbackData, prefix='goto_stage'):
    stage: CreateStagesNames


"""
Keyboards
"""

complete_builer = InlineKeyboardBuilder(
    [[InlineKeyboardButton(text='Завершить', callback_data=CompleteCreateProduct().pack())]])


async def gen_next_builer(stage: CreateStagesNames) -> InlineKeyboardBuilder:
    next_markup = InlineKeyboardBuilder(
        [[InlineKeyboardButton(text='Назад', callback_data=GotoStage(stage=stage).pack())]])
    return next_markup

"""
Message handlers
"""

@router.message(F.text == '/new_product', state='*')
async def on_new_product(message: Message, state: FSMContext):
    await message.answer('<b>Введите название товара</b>\n'
                         '<i>Оно будет отображаться в магазине у пользователей</i>\n'
                         '<i>Вы сможете поменять его в меню редактировании товаров</i>\n')
    await state.set_state(CreateProductStates.name)


@router.message(state=CreateProductStates.name)
async def enter_name(message: Message, state: FSMContext, skip_enter=False):
    if not skip_enter:
        product_data = (await state.get_data()).get('product_data') or {}
        product_data['name'] = message.text
        await state.update_data(product_data=product_data)
    markup = (await gen_next_builer(CreateStagesNames.name)).as_markup()
    await message.answer('<b>Введите категорию товара</b>\n'
                         '<i>Она будет отображаться в магазине у пользователей</i>\n'
                         '<i>Вы сможете поменять её в меню редактировании товаров</i>\n',
                         reply_markup=markup)
    await state.set_state(CreateProductStates.category)


@router.message(state=CreateProductStates.category)
async def enter_category(message: Message, state: FSMContext, skip_enter=False):
    if not skip_enter:
        product_data = (await state.get_data()).get('product_data') or {}
        product_data['category'] = message.text
        await state.update_data(product_data=product_data)
    markup = (await gen_next_builer(CreateStagesNames.category)).as_markup()
    await message.answer('<b>Введите стоимость товара</b>\n'
                         '<i>Она будет отображаться в магазине у пользователей</i>\n'
                         '<i>Вы сможете поменять её в меню редактировании товаров</i>\n',
                         reply_markup=markup)
    await state.set_state(CreateProductStates.price)


@router.message(F.text.isdigit(), state=CreateProductStates.price)
async def enter_price(message: Message, state: FSMContext):
    product_data = (await state.get_data()).get('product_data') or {}
    product_data['price'] = int(message.text)
    markup = (await gen_next_builer(CreateStagesNames.price))
    markup.add(*complete_builer.buttons)
    markup = markup.as_markup()
    await state.set_state(CreateProductStates.complete)
    await message.answer('<b>Для подтверждения создания нажмите кнопку \'Завершить\'</b>\n\n'
                         f'<b>Создание продукта</b>\n'
                         f'<b>Название:</b> <code>{product_data.get("name")}</code>\n'
                         f'<b>Категория:</b> <code>{product_data.get("category")}</code>\n'
                         f'<b>Стоимость:</b> <code>{product_data.get("price")}</code>\n\n'
                         f'<i></i>', reply_markup=markup)


"""
Stages
"""

CreateStages = {

    CreateStagesNames.name: on_new_product,
    CreateStagesNames.price: enter_category,
    CreateStagesNames.category: enter_name
}

"""
CallbackQuery handlers
"""


@router.callback_query(GotoStage.filter())
async def on_goto_stage(query: CallbackQuery, callback_data: GotoStage, state: FSMContext):
    try:
        await CreateStages.get(callback_data.stage)(query.message, state, skip_enter=True)
    except TypeError:
        await CreateStages.get(callback_data.stage)(query.message, state)


@router.callback_query(CompleteCreateProduct().filter(), state=CreateProductStates.complete)
async def on_complete(query: CallbackQuery, state: FSMContext, db_session):
    product_data = (await state.get_data()).get('product_data')
    product = await Product.add_product(**product_data, session=db_session)
    await query.message.answer(f'<b>Создан продукт с ID:</b> <code>{product.id}</code>')
    await state.clear()
