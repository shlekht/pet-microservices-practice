from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from payment_service.infrastructure.database import async_session_maker
from payment_service.infrastructure.rabbitmq import RabbitMQ
from payment_service.service import PaymentService


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]

async def get_rabbit(request: Request) -> RabbitMQ:
    """It takes our lifespan-initialized rabbit client from app.state"""
    rabbit_backend = getattr(request.app.state, "rabbit", None)
    if rabbit_backend is None:
        raise RuntimeError("Rabbit client is not initialized.")
    return rabbit_backend

RabbitMQDependency = Annotated[RabbitMQ, Depends(get_rabbit)]

async def get_payment_service(session: SessionDependency, broker: RabbitMQDependency) -> PaymentService:
    return PaymentService(session, broker)