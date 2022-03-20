from typing import Set, List

from sqlalchemy import Column, Integer, Sequence, BigInteger, insert, select, String, delete, update
from sqlalchemy.orm import Session

from tgbot.models.database import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer(), Sequence('products_seq'), primary_key=True, nullable=False)
    name = Column(String(), nullable=False)
    category = Column(String(), nullable=False)
    price = Column(BigInteger(), nullable=False)

    @classmethod
    async def add_product(cls, name: str, price: int, category: str, session: Session):
        result = await session.execute(insert(Product).values(name=name, price=price, category=category))
        product = await cls.get_product(result.inserted_primary_key[0], session)
        await session.commit()
        return product

    @classmethod
    async def remove_product(cls, product, session: Session):
        result = await session.execute(delete(Product).where(Product.id == product.id))
        await session.commit()

    @classmethod
    async def get_product(cls, id: int, session: Session):
        product = (await session.execute(select(Product).where(Product.id == id))).scalar()
        return product

    @classmethod
    async def get_products(cls, session: Session) -> list:
        return (await session.execute(select(Product))).scalars().all()

    @classmethod
    async def get_products_by_category(cls, category: str, session: Session) -> list:
        return (await session.execute(select(Product).where(Product.category == category))).scalars().all()

    @classmethod
    async def get_categories(cls, session: Session) -> List[str]:
        categories = []
        products = await cls.get_products(session)
        for product in products:
            if product.category not in categories:
                categories.append(product.category)
        return categories

    async def get_info(self):
        return ('<b>Информация о продукте</b>\n'
                f'<code>{self.name}</code>\n\n'
                f'<b>Цена:</b> {self.price}\n'
                f'<b>Категория: </b><code>{self.category}</code>\n')

    async def update_name(self, name: str, session: Session):
        await session.execute(update(Product).where(Product.id == self.id).values(name=name))
        await session.refresh(self)
        await session.commit()

    async def update_category(self, category: str, session: Session):
        await session.execute(update(Product).where(Product.id == self.id).values(category=category))
        await session.refresh(self)
        await session.commit()

    async def update_price(self, price: int, session: Session):
        await session.execute(update(Product).where(Product.id == self.id).values(price=price))
        await session.refresh(self)
        await session.commit()
