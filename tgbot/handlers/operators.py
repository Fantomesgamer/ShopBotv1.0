from aiogram import Router, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.filters.role import IsSuperUser
from tgbot.models import User

router = Router()


@router.message(IsSuperUser(), F.text == '/operators', state='*')
async def on_operators(message: Message, db_session):
    await message.answer(await User.gen_operators_list(db_session))
