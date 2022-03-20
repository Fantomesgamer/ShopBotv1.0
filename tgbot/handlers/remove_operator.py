from aiogram import Router, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from sqlalchemy.orm import Session

from tgbot.filters.role import IsSuperUser
from tgbot.models import User

router = Router()

"""
States
"""


class RemoveOperatorStates(StatesGroup):
    user_id = State()


"""
Messages handlers
"""


@router.message(IsSuperUser(), F.text == '/remove_operator', state='*')
async def on_set_operator(message: Message, state: FSMContext):
    await message.answer('<b>Введите Telegram-ID оператора</b>\n'
                         '<i>Узнать список ID операторов можно командой: </i>/operators\n'
                         '<i>Для отмены, пиши:</i> /cancel\n')
    await state.set_state(RemoveOperatorStates.user_id)


@router.message(IsSuperUser(), F.text.regexp('\d+'), state=RemoveOperatorStates.user_id)
async def enter_user_id(message: Message, state: FSMContext, db_session: Session):
    user = await User.get_user_by_user_id(int(message.text), db_session)
    if user:
        if user.is_operator:
            await user.set_operator(False, db_session)
            await message.answer(f'<b>Теперь пользователь не имеет статуса оператора!</b>\n'
                                 f'<b>ID пользователя:</b> <code>{user.user_id}</code>\n\n'
                                 '<i>Если хотите вернуть оператора, воспользуйтесь командой:</i> '
                                 '/set_operator\n\n'
                                 '<i>Оператор может создавать новые товары с помощью команды '
                                 '/new_product, а так-же '
                                 'получать уведомления при оформлении покупок!</i>')
            await state.clear()
        else:
            await message.answer('<b>Данный пользователь не является оператором!</b>\n'
                                 '<i>Посмотреть список ID операторов:</i> /operators\n'
                                 '<i>Добавить оператора:</i> /set_operator\n')
    else:
        await message.answer('<b>Оператор не найден</b>\n'
                             '<i>Узнать список ID операторов можно командой: </i>/operators\n'
                              '<i>Для отмены, пиши:</i> /cancel\n')


@router.message(IsSuperUser(), state=RemoveOperatorStates.user_id)
async def not_valid_user_id(message: Message):
    await message.answer('<b>Telegram ID пользователя - это положительное число.\n</b>'
                         '<b>Например:</b> <code>122312</code>\n\n'
                         '<i>Для отмены, пиши:</i> /cancel')
