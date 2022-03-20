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


class SetOperatorStates(StatesGroup):
    user_id = State()


"""
Messages handlers
"""


@router.message(IsSuperUser(), F.text == '/set_operator', state='*')
async def on_set_operator(message: Message, state: FSMContext):
    await message.answer('<b>Введите Telegram-ID пользователя, зарегестрированного в боте</b>\n'
                         '<i>Узнать свой Telegram-ID можно у бота:</i> @myidbot\n'
                         '<i>Для отмены, пиши:</i> /cancel\n')
    await state.set_state(SetOperatorStates.user_id)


@router.message(IsSuperUser(), F.text.regexp('\d+'), state=SetOperatorStates.user_id)
async def enter_user_id(message: Message, state: FSMContext, db_session: Session):
    user = await User.get_user_by_user_id(int(message.text), db_session)
    if user:
        if not user.is_operator:
            await user.set_operator(True, db_session)
            await message.answer(f'<b>Теперь пользователь имеет статус оператора!</b>\n'
                                 f'<b>ID пользователя:</b> <code>{user.user_id}</code>\n\n'
                                 '<i>Если хотите удалить оператора, воспользуйтесь командой:</i> '
                                 '/remove_operator\n\n'
                                 '<i>Оператор может создавать новые товары с помощью команды '
                                 '/new_product, а так-же '
                                 'получать уведомления при оформлении покупок!</i>')
            await state.clear()
        else:
            await message.answer('<b>Данный пользователь уже является оператором!</b>\n'
                                 '<i>Посмотреть список ID операторов:</i> /operators\n'
                                 '<i>Удалить оператора:</i> /remove_operator\n')
    else:
        await message.answer('<b>Пользователь не найден</b>\n'
                             '<i>Введите Telegram-ID пользователя, <b>зарегестрированного</b> в боте</i>\n'
                             '<i>Узнать свой Telegram-ID можно у бота:</i> @myidbot\n')


@router.message(IsSuperUser(), state=SetOperatorStates.user_id)
async def not_valid_user_id(message: Message):
    await message.answer('<b>Telegram ID пользователя - это положительное число.\n</b>'
                         '<b>Например:</b> <code>122312</code>\n\n'
                         '<i>Для отмены, пиши:</i> /cancel')
