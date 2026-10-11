from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select

from auth_service.dependencies import SessionDependency
from auth_service.infrastructure.database import Base, engine
from auth_service.models import User
from auth_service.schemas import (
    TokenResponseSchema,
    UserLoginSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from auth_service.security import create_access_token, hash_password, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterSchema,
    db_session: SessionDependency,
) -> TokenResponseSchema:
    hashed_password = hash_password(payload.password)
    user = User(email=payload.email, hashed_password=hashed_password)
    db_session.add(user)
    await db_session.commit()

    access_token = create_access_token(user)
    return TokenResponseSchema(
        access_token=access_token, user=UserReadSchema.model_validate(user)
    )


@app.post("/login", status_code=status.HTTP_200_OK)
async def login(
    payload: UserLoginSchema,
    db_session: SessionDependency,
) -> TokenResponseSchema:
    user = await db_session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user)
    return TokenResponseSchema(
        access_token=access_token, user=UserReadSchema.model_validate(user)
    )
