import asyncio
from uuid import uuid4

from aio_pika.abc import AbstractExchange
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from payment_service.config import settings
from payment_service.infrastructure.rabbitmq import RabbitMQ
from payment_service.models import Payment, Status
from payment_service.schemas import PaymentCreateSchema, PaymentReadSchema


class PaymentService:
    def __init__(self, session: AsyncSession, broker: RabbitMQ):
        self.session = session
        self.broker = broker

    async def get_all_payments(self) -> list[PaymentReadSchema]:
        try:
            result = await self.session.execute(select(Payment))
            payments = result.scalars().all()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print("Get payments error: ", e)
            raise

        return [PaymentReadSchema.model_validate(payment) for payment in payments]

    async def create_payment(self, payload: PaymentCreateSchema) -> Payment:

        payment_to_add = Payment(
            order_id=payload.order_id,
            status=Status.CREATED,
            total_price=payload.total_price,
        )

        try:
            self.session.add(payment_to_add)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            print("Create payment error: ", e)
            raise

        return payment_to_add

    async def complete_payment(
        self, payment: Payment, order_id: int, exchange: AbstractExchange
    ) -> None:
        await asyncio.sleep(3)  # Имитация оплаты
        payment.status = Status.PAID
        await self.session.commit()

        event = {
            "event_id": str(uuid4),
            "order_id": order_id,
            "status": Status.PAID,
        }

        await self.broker.event_publish_json(
            exchange, settings.payment_succeeded_routing_key, event
        )
