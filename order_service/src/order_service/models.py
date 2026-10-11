import datetime
import enum

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from order_service.infrastructure.database import Base


class Status(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CREATED = "CREATED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[Status]
    total_price: Mapped[int]
    user_id: Mapped[int]

    items: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False,
    )
