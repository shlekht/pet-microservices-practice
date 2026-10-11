from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from order_service.http_client import PaymentHTTPClient
from order_service.infrastructure.database import async_session_maker
from order_service.schemas import CurrentUserSchema
from order_service.security import decode_access_token
from order_service.service import OrderService


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]

def get_payment_http_client(request: Request) -> PaymentHTTPClient:
    return request.app.state.payment_http_client

PaymentHTTPClientDependency = Annotated[
    PaymentHTTPClient,
    Depends(get_payment_http_client),
]

async def get_order_service(session: SessionDependency, payment_http_client: PaymentHTTPClientDependency) -> OrderService:
    return OrderService(session, payment_http_client)




bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
) -> CurrentUserSchema:
    token = credentials.credentials

    payload = decode_access_token(token)

    return CurrentUserSchema(
        id=payload["sub"],
        email=payload["email"]
    )