import datetime
import enum

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from payment_service.infrastructure.database import Base


class Status(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CREATED = "CREATED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int]
    status: Mapped[Status]
    total_price: Mapped[int]

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False,
    )
