from pydantic import BaseModel, ConfigDict

from payment_service.models import Status


class PaymentCreateSchema(BaseModel):
    order_id: int
    total_price: int


class PaymentReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    status: Status
    total_price: int
