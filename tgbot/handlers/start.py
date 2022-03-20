from aiogram import F, Router

router = Router()

@router.message(F.text == '/start', state='*')
async def on_start(message, state):
    await message.answer('Добро пожаловать в бота для отслеживания отзывов на WB!234')
    await state.clear()