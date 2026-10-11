from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, status

from order_service.config import settings
from order_service.dependencies import get_current_user, get_order_service
from order_service.http_client import PaymentHTTPClient
from order_service.infrastructure.database import Base, engine
from order_service.infrastructure.rabbitmq import RabbitMQ
from order_service.models import Order
from order_service.schemas import CurrentUserSchema, OrderCreateSchema, OrderReadSchema
from order_service.service import OrderService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # HTTP Client
    app.state.payment_http_client = PaymentHTTPClient(
        base_url=settings.PAYMENT_API_URL,
    )

    # RabbitMQ
    broker = RabbitMQ(url=settings.RABBITMQ_URL)
    await broker.connect()
    channel = await broker.create_channel()
    payment_exchange = await broker.declare_payment_exchange(
        channel=channel, exchange_name=settings.payment_exchange_name
    )
    await broker.start_payments_consume(payment_exchange)
    app.state.rabbit = broker
    app.state.payment_exchange = payment_exchange

    yield

    await engine.dispose()
    await broker.close()
    await app.state.payment_http_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/orders", status_code=status.HTTP_200_OK)
async def get_all_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderReadSchema]:
    return await service.get_all_orders()


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateSchema,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[CurrentUserSchema, Depends(get_current_user)],
) -> OrderReadSchema:
    return await service.create_order(payload=payload, user_id=current_user.id)
