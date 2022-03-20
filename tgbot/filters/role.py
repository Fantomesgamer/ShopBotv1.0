from typing import Any, Union, Dict

from aiogram.dispatcher.filters import BaseFilter


class IsSuperUser(BaseFilter):
    async def __call__(self, message, user, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        print(user.is_superuser)
        return user.is_superuser


class IsOperator(BaseFilter):
    async def __call__(self, message, user, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        return user.is_operator
