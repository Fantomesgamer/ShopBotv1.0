from sqlalchemy import Column, Integer, Sequence, BigInteger, insert, select, Boolean, update, String
from sqlalchemy.orm import Session

from tgbot.config import load_config
from tgbot.models.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), Sequence('users_seq'), primary_key=True, nullable=False)
    user_id = Column(BigInteger(), unique=True, nullable=False)
    username = Column(String(), nullable=False)
    is_operator = Column(Boolean(), default=False)
    config = load_config('bot.ini')

    @property
    def is_superuser(self) -> bool:
        return self.user_id == User.config.tg_bot.super_user

    @classmethod
    async def add_user(cls, user_id: int, username: str, session: Session):
        result = await session.execute(insert(User).values(user_id=user_id, username=username))
        user = await cls.get_user_by_id(result.inserted_primary_key[0], session)
        await session.commit()
        return user

    @classmethod
    async def get_users(cls, is_operator: bool, session: Session):
        if is_operator:
            return (await session.execute(select(User).where(User.is_operator == True))).scalars().all()
        return (await session.execute(select(User))).scalars().all()

    @classmethod
    async def get_user_by_user_id(cls, user_id: int, session: Session):
        user = (await session.execute(select(User).where(User.user_id == user_id))).scalar()
        return user

    @classmethod
    async def get_user_by_id(cls, id: int, session: Session):
        user = (await session.execute(select(User).where(User.id == id))).scalar()
        return user

    async def set_operator(self, value: bool, session: Session):
        await session.execute(update(User).where(User.id == self.id).values(is_operator=value))
        await session.refresh(self)
        await session.commit()

    @classmethod
    async def gen_operators_list(cls, db_session: Session) -> str:
        operators = await User.get_users(is_operator=True, session=db_session)
        text = f'<b>Операторы ({len(operators)})</b>\n\n' + '\n'.join([f'\n<code>{operator.username} {operator.user_id}</code>' for operator in operators])
        return text