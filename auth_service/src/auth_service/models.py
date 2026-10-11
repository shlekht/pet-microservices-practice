import datetime

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from auth_service.infrastructure.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False,
    )
