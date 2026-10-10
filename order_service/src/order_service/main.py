from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, status

from order_service.dependencies import get_order_service
from order_service.infrastructure.database import Base, engine
from order_service.models import Order
from order_service.schemas import OrderCreateSchema, OrderReadSchema
from order_service.service import OrderService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


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
) -> OrderReadSchema:
    return await service.create_order(payload)
