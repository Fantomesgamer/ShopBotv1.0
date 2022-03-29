import asyncio

from aiogram.types import BotCommand, BotCommandScope, BotCommandScopeChat

from tgbot.config import load_config
from aiogram import Dispatcher, Bot

from tgbot.models.database import create_pool
from loguru import logger
from tgbot.middlewares.db_middleware import DbMiddleware
from tgbot.middlewares.authorize import AuthorizeMiddleware
from tgbot.models.database import router as db_router
from tgbot.handlers.start import router as start_router

from tgbot.handlers.set_operator import router as set_operator
from tgbot.handlers.select_operator import router as select_operator
from tgbot.handlers.connect_operator import router as connect_operator
from tgbot.handlers.remove_operator import router as remove_operator
from tgbot.handlers.new_product import router as new_product
from tgbot.handlers.set_message import router as set_message
from tgbot.handlers.price_list import router as price_list
from tgbot.handlers.operators import router as operators
from tgbot.handlers.menu import router as menu
from tgbot.handlers.cancel import router as cancel


async def main():
    config = load_config('bot.ini')

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

    dispatcher = Dispatcher()

    pool = await create_pool()

    dispatcher.include_router(db_router)
    dispatcher.message.outer_middleware(DbMiddleware(pool))
    dispatcher.message.outer_middleware(AuthorizeMiddleware())
    dispatcher.callback_query.outer_middleware(DbMiddleware(pool))
    dispatcher.callback_query.outer_middleware(AuthorizeMiddleware())

    default_commands = [BotCommand(command='/shop',
                                   description='Открыть меню товаров'),
                        BotCommand(command='/menu',
                                   description='Вызвать главное меню'),
                        ]
    #
    # admin_commands = [BotCommand(command='/mailing', description='Админ команда для создания рассылки'),
    #                   BotCommand(command='/set_limit', description='Админ команда для изменения лимита товаров')]
    # admin_commands.extend(default_commands)
    #
    db_router.pool = pool
    # #
    # # session = pool()
    await bot.set_my_commands(default_commands)
    # # for user in await User.get_users(session):
    # #     if user.is_admin:
    # #         await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=user.user_id))
    # # await session.close()
    dispatcher.include_router(start_router)
    dispatcher.include_router(menu)
    dispatcher.include_router(cancel)
    dispatcher.include_router(connect_operator)
    dispatcher.include_router(set_operator)
    dispatcher.include_router(select_operator)
    dispatcher.include_router(remove_operator)
    dispatcher.include_router(new_product)
    dispatcher.include_router(set_message)
    dispatcher.include_router(price_list)
    dispatcher.include_router(operators)


    logger.info(f'Bot {(await bot.get_me()).username} was started!')
    try:
        await dispatcher.start_polling(bot)
    finally:
        logger.error(f'Bot {(await bot.get_me()).username} was stopped!')
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
