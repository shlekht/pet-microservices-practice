from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.models import Order, Status
from order_service.schemas import OrderCreateSchema, OrderReadSchema


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_orders(self) -> list[OrderReadSchema]:
        try:
            result = await self.session.execute(select(Order))
            orders = result.scalars().all()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print("Get orders error: ", e)
            raise

        return [OrderReadSchema.model_validate(order) for order in orders]

    async def create_order(self, payload: OrderCreateSchema) -> OrderReadSchema:
        items = [item.model_dump() for item in payload.items]

        total_price = sum(item["price"] for item in items)

        order_to_add = Order(
            status=Status.PENDING, total_price=total_price, items=items
        )
        try:
            self.session.add(order_to_add)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print("Create order error: ", e)
            raise

        return OrderReadSchema.model_validate(order_to_add)
