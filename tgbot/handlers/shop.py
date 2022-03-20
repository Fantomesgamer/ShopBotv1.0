from random import choice
from typing import Tuple

from aiogram import Router, types, F, Bot
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.orm import Session
from enum import Enum
from aiogram.exceptions import TelegramBadRequest
from tgbot.handlers.cancel import cancel_markup, cancel_button
from tgbot.handlers.menu import MenuChoice, MenuActions
from tgbot.models import Product, User

router = Router()

"""
Misc
"""


def update_page(page: int, max_page: int) -> int | None:
    match (int(max_page), int(page)):
        case 0:
            return None
        case max_page, page if max_page < page:
            return 1
        case max_page, page if max_page > page:
            return max_page
        case _:
            return page


class EditTypes(str, Enum):
    price = 'PRICE'
    category = 'CATEGORY'
    name = 'NAME'
    remove = 'REMOVE'


"""
States
"""


class ShopStates(StatesGroup):
    confirm = State()
    price = State()
    name = State()
    category = State()


"""
CallbackData
"""


class GotoPage(CallbackData, prefix='goto_page'):
    page: int
    category: str


class ShowCategories(CallbackData, prefix='show_categories'):
    pass


class EditProduct(CallbackData, prefix='edit_product'):
    product_id: int
    edit_type: EditTypes


class ConnectOperator(CallbackData, prefix='connect_operator'):
    product_id: int
    user_id: int


class Confirm(CallbackData, prefix='confirm'):
    confirm_type: EditTypes


"""
Keyboards
"""


async def gen_category_markup(db_session: Session) -> InlineKeyboardMarkup | None:
    categories = await Product.get_categories(db_session)
    if len(categories) == 0:
        return None
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.add(InlineKeyboardButton(text=category, callback_data=GotoPage(category=category, page=1).pack()))
    return builder.as_markup()


async def gen_shop_markup(category: str, db_session: Session, user: User, page: int = 1) -> Tuple[
                                                                                                InlineKeyboardMarkup, Product] | None:
    products = await Product.get_products_by_category(category, db_session)
    max_page = len(products)
    page = update_page(page, max_page)
    if not page or len(products) <= 0:
        return None

    builder = InlineKeyboardBuilder()
    product = products[page - 1]

    if user.is_operator:
        builder.row(
            InlineKeyboardButton(text='Изменить категорию',
                                 callback_data=EditProduct(product_id=product.id, edit_type=EditTypes.category).pack()),
            InlineKeyboardButton(text='Изменить название',
                                 callback_data=EditProduct(product_id=product.id, edit_type=EditTypes.name).pack()),
            InlineKeyboardButton(text='Изменить цену',
                                 callback_data=EditProduct(product_id=product.id, edit_type=EditTypes.price).pack()))
        builder.row(
            InlineKeyboardButton(text='Удалить',
                                 callback_data=EditProduct(product_id=product.id, edit_type=EditTypes.remove).pack()))

    builder.row(
        InlineKeyboardButton(text='Связаться с оператором', callback_data=ConnectOperator(product_id=product.id,
                                                                                          user_id=user.id).pack()),
        InlineKeyboardButton(text='Назад к списку категорий', callback_data=ShowCategories().pack()))

    builder.row(
        InlineKeyboardButton(text='<<<', callback_data=GotoPage(page=page - 1, category=category).pack()),
        InlineKeyboardButton(text=f'{page}/{max_page}', callback_data='page'),
        InlineKeyboardButton(text='>>>', callback_data=GotoPage(page=page + 1, category=category).pack()))

    return builder.as_markup(), product


async def gen_confirm_markup(confirm_type: EditTypes) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Подтвердить', callback_data=Confirm(confirm_type=confirm_type).pack()),
                cancel_button)
    return builder.as_markup()

async def gen_user_url_markup(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder([[InlineKeyboardButton(text='Связаться',url=url)]]).as_markup()

"""
Message Handlers
"""


@router.message(F.text == '/shop', state='*')
@router.callback_query(MenuChoice.filter(F.action == MenuActions.shop), state='*')
async def on_shop(query: CallbackQuery, state: FSMContext, user: User, db_session: Session):
    markup = await gen_category_markup(db_session)
    message = query.message
    if not markup:
        return await message.answer('<b>Список товаров пуст</b>', reply_markup=markup)
    await message.answer('<b>Категории</b>', reply_markup=markup)


"""
CallbackQuery Handlers
"""


@router.callback_query(GotoPage.filter(), state='*')
async def goto_page(query: CallbackQuery, state: FSMContext, callback_data: GotoPage, user: User, db_session):
    markup, product = await gen_shop_markup(callback_data.category, db_session, user, callback_data.page)
    try:
        if not markup:
            return await query.message.edit_text(text='<b>Список товаров пуст</b>', reply_markup=markup)
        await query.message.edit_text(text=await product.get_info(), reply_markup=markup)
    except TelegramBadRequest:
        pass


@router.callback_query(EditProduct.filter(F.edit_type == EditTypes.remove), state='*')
async def on_remove_product(query: CallbackQuery, state: FSMContext, callback_data: EditProduct, db_session):
    message = query.message
    await message.answer('<b>Удалить товар?</b>\n'
                         '<i>Восстановление невозможно</i>',
                         reply_markup=await gen_confirm_markup(callback_data.edit_type))
    await state.update_data(product_id=callback_data.product_id)
    await state.set_state(ShopStates.confirm)


@router.callback_query(EditProduct.filter(F.edit_type == EditTypes.name), state='*')
async def on_edit_name(query: CallbackQuery, state: FSMContext, callback_data: EditProduct):
    message = query.message
    await message.answer('<b>Введите новое название товара для изменения</b>', reply_markup=cancel_markup)
    await state.update_data(product_id=callback_data.product_id)
    await state.set_state(ShopStates.name)


@router.message(state=ShopStates.name)
async def enter_name(message: Message, state: FSMContext):
    await message.answer('<b>Установить новое имя для товара?</b>',
                         reply_markup=await gen_confirm_markup(EditTypes.name))
    await state.update_data(name=message.text)
    await state.set_state(ShopStates.confirm)


@router.callback_query(Confirm.filter(F.confirm_type == EditTypes.name), state=ShopStates.confirm)
async def confirm_name(query: CallbackQuery, state: FSMContext, callback_data: Confirm, db_session: Session):
    data = await state.get_data()
    message = query.message
    product = await Product.get_product(data.get('product_id'), db_session)
    if product:
        await product.update_name(data.get('name'), db_session)
        return await message.answer('<b>Имя обновлено</b>')
    await message.answer('<b>Товар не найден</b>')


@router.callback_query(EditProduct.filter(F.edit_type == EditTypes.category), state='*')
async def on_edit_category(query: CallbackQuery, state: FSMContext, callback_data: EditProduct):
    message = query.message
    await message.answer('<b>Введите новую категорию для изменения</b>', reply_markup=cancel_markup)
    await state.update_data(product_id=callback_data.product_id)
    await state.set_state(ShopStates.category)


@router.message(state=ShopStates.category)
async def enter_category(message: Message, state: FSMContext):
    await message.answer('<b>Установить новую категорию для товара?</b>',
                         reply_markup=await gen_confirm_markup(EditTypes.category))
    await state.update_data(category=message.text)
    await state.set_state(ShopStates.confirm)


@router.callback_query(Confirm.filter(F.confirm_type == EditTypes.category), state=ShopStates.confirm)
async def confirm_category(query: CallbackQuery, state: FSMContext, callback_data: Confirm, db_session: Session):
    data = await state.get_data()
    message = query.message
    product = await Product.get_product(data.get('product_id'), db_session)
    if product:
        await product.update_category(data.get('category'), db_session)
        return await message.answer('<b>Категория обновлена</b>')
    await message.answer('<b>Товар не найден</b>')


@router.callback_query(EditProduct.filter(F.edit_type == EditTypes.price), state='*')
async def on_edit_price(query: CallbackQuery, state: FSMContext, callback_data: EditProduct):
    message = query.message
    await message.answer('<b>Введите новую стоимость для изменения</b>', reply_markup=cancel_markup)
    await state.update_data(product_id=callback_data.product_id)
    await state.set_state(ShopStates.price)


@router.message(F.text.isdigit(),state=ShopStates.price)
async def enter_price(message: Message, state: FSMContext):
    await message.answer('<b>Установить новую стоимость для товара?</b>',
                         reply_markup=await gen_confirm_markup(EditTypes.price))
    await state.update_data(price=int(message.text))
    await state.set_state(ShopStates.confirm)


@router.callback_query(Confirm.filter(F.confirm_type == EditTypes.price), state=ShopStates.confirm)
async def confirm_price(query: CallbackQuery, state: FSMContext, callback_data: Confirm, db_session: Session):
    data = await state.get_data()
    message =  query.message
    product = await Product.get_product(data.get('product_id'), db_session)
    if product:
        await product.update_price(data.get('price'), db_session)
        return await message.answer('<b>Стоимость обновлена</b>')
    await message.answer('<b>Товар не найден</b>')


@router.callback_query(Confirm.filter(F.confirm_type == EditTypes.remove))
async def confirm_remove(query: CallbackQuery, state: FSMContext, callback_data: Confirm, db_session):
    product = await Product.get_product((await state.get_data()).get('product_id'), db_session)
    if product:
        await Product.remove_product(product, db_session)
        await query.message.answer('<b>Товар удалён</b>')
    else:
        await query.message.answer('<b>Товар не найден</b>')

@router.callback_query(ConnectOperator.filter(), state='*')
async def on_connect_operator(query: CallbackQuery, state: FSMContext, callback_data: ConnectOperator, db_session, bot: Bot):
    username = query.from_user.username
    message = query.message
    if username:
        url = f't.me/{username}'
        product = await Product.get_product(callback_data.product_id, db_session)
        if not product:
            return await message.answer('<b>Товар не найден</b>')
        operators = await User.get_users(is_operator=True, session=db_session)

        if len(operators) > 0:
            operator = choice(operators)
            await bot.send_message(chat_id=operator.user_id, text='<b>Новая заявка на покупку</b>\n\n'
                                                                  f'<b>Информация о товаре</b>\n'
                                                                  f'<b>Название:</b><code>{product.name}</code>\n'
                                                                  f'<b>Категория:</b><code>{product.category}</code>\n'
                                                                  f'<b>Стоимость:</b><code>{product.price}</code>\n',
                                   reply_markup=await gen_user_url_markup(url))
        else:
            await message.answer('<b>Не найдено доступных операторов, обратитесь позже</b>\n')
    else:
        message.answer('<b>Не заполнен username</b>\n'
                      '<i>Для того чтобы связаться с оператором для оформления заказа, вам необходимо иметь username. \n'
                       'Указать его можно в настройках телеграма.</i>')

@router.callback_query(ShowCategories.filter(), state='*')
async def show_categories(query: CallbackQuery, state: FSMContext, callback_data: ShowCategories, db_session):
    markup = await gen_category_markup(db_session)
    if not markup:
        return await query.message.edit_text('<b>Список товаров пуст</b>', reply_markup=markup)
    await query.message.edit_text('<b>Категории</b>', reply_markup=markup)
