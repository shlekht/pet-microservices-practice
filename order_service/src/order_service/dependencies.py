from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.infrastructure.database import async_session_maker
from order_service.service import OrderService


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def get_order_service(session: SessionDependency) -> OrderService:
    return OrderService(session)