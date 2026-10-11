import json

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractRobustConnection,
)
from order_service.config import settings
from order_service.infrastructure.database import async_session_maker
from order_service.models import Order, Status


class RabbitMQ:
    def __init__(self, url: str):
        self.url = url
        self.connection: AbstractRobustConnection | None = None

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(url=self.url)

    async def create_channel(self) -> AbstractChannel:
        if self.connection is None:
            raise RuntimeError("Not connected")

        return await self.connection.channel()

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def declare_payment_exchange(
            self, channel: AbstractChannel, exchange_name: str
        ):
            return await channel.declare_exchange(exchange_name)


    # было бы правильнее вынести куда-нибудь отдельно следующие функции

    async def _handle_payment_events(self, message: AbstractIncomingMessage): 
        async with message.process():
            event = json.loads(message.body.decode("utf-8"))
            async with async_session_maker() as session:
                order = await session.get(Order, event["order_id"])
                if order is not None:
                    order.status = Status.PAID
                await session.commit()

    async def start_payments_consume(self, payment_exchange: AbstractExchange):
        if self.connection is not None:
            payment_channel = await self.connection.channel()
            payment_queue = await payment_channel.declare_queue(settings.payment_queue_name)
            await payment_queue.bind(payment_exchange, routing_key=settings.payment_succeeded_routing_ley)
            await payment_queue.consume(self._handle_payment_events)