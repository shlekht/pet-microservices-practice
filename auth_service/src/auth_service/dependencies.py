from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.infrastructure.database import async_session_maker


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
