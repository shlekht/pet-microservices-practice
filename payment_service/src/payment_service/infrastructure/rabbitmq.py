import json

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractRobustConnection,
)


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
        await channel.declare_exchange(exchange_name)

    async def event_publish_json(
        self, exchange: AbstractExchange, routing_key: str, data: dict
    ):
        message = aio_pika.Message(json.dumps(data).encode())
        await exchange.publish(message, routing_key)
