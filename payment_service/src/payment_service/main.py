from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status

from payment_service.config import settings
from payment_service.dependencies import get_payment_service
from payment_service.infrastructure.database import Base, engine
from payment_service.infrastructure.rabbitmq import RabbitMQ
from payment_service.schemas import PaymentCreateSchema, PaymentReadSchema
from payment_service.service import PaymentService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    broker = RabbitMQ(url=settings.RABBITMQ_URL)
    await broker.connect()
    channel = await broker.create_channel()
    payment_exchange = await broker.declare_payment_exchange(
        channel=channel, exchange_name=settings.payment_exchange_name
    )
    app.state.rabbit = broker
    app.state.payment_exchange = payment_exchange

    yield

    await engine.dispose()
    await broker.close()


app = FastAPI(lifespan=lifespan)


@app.get("/payments", status_code=status.HTTP_200_OK)
async def get_all_payments(
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> list[PaymentReadSchema]:
    return await service.get_all_payments()


@app.post("/payments", status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: Request,
    payload: PaymentCreateSchema,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentReadSchema:

    payment = await service.create_payment(payload)
    await service.complete_payment(
        payment=payment,
        order_id=payload.order_id,
        exchange=request.app.state.payment_exchange,
    )
    return PaymentReadSchema.model_validate(payment)
