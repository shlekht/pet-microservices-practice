from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.http_client import PaymentHTTPClient
from order_service.models import Order, Status
from order_service.schemas import (
    OrderCreateSchema,
    OrderReadSchema,
    PaymentCreateSchema,
)


class OrderService:
    def __init__(self, session: AsyncSession, payment_http_client: PaymentHTTPClient):
        self.session = session
        self.payment_http_client = payment_http_client

    async def get_all_orders(self) -> list[OrderReadSchema]:
        try:
            result = await self.session.execute(select(Order))
            orders = result.scalars().all()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print("Get orders error: ", e)
            raise

        return [OrderReadSchema.model_validate(order) for order in orders]

    async def create_order(
        self, payload: OrderCreateSchema, user_id: int
    ) -> OrderReadSchema:
        items = [item.model_dump() for item in payload.items]

        total_price = sum(item["price"] for item in items)

        order_to_add = Order(
            status=Status.PENDING, user_id=user_id, total_price=total_price, items=items
        )
        try:
            self.session.add(order_to_add)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print("Create order error: ", e)
            raise

        data_for_payment = PaymentCreateSchema(
            order_id=order_to_add.id, total_price=order_to_add.total_price
        )
        await self.payment_http_client.create_payment(data_for_payment)

        return OrderReadSchema.model_validate(order_to_add)
