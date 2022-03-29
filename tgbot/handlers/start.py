from aiogram import F, Router

from tgbot.handlers.menu import on_menu
from tgbot.handlers.set_message import get_message

router = Router()


@router.message(F.text == '/start', state='*')
async def on_start(message, state, user):
    await message.answer((await get_message('start')))
    await on_menu(message, state=state, user=user)
    await state.clear()
