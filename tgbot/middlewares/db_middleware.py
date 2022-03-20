from typing import Callable, Any, Dict, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker, Session


class DbMiddleware(BaseMiddleware):

    def __init__(self, pool):
        self.pool: sessionmaker = pool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        db_session: Session = self.pool()
        data['db_session'] = db_session

        try:
            await handler(event, data)
        finally:
            await db_session.close()
