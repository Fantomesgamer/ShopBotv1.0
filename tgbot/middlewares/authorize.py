from typing import Callable, Any, Dict, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from loguru import logger
from sqlalchemy.orm import sessionmaker, Session


from tgbot.models.user import User


class AuthorizeMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        db_session = data.get('db_session')
        user = await User.get_user_by_user_id(event.from_user.id, db_session)
        if not user:

            user = await User.add_user(event.from_user.id, event.from_user.username,db_session)
            logger.info(f'Registered new user! {user}')
        data['user'] = user

        await handler(event, data)

