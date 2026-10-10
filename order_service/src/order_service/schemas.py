from pydantic import BaseModel, ConfigDict

from order_service.models import Status


class ItemSchema(BaseModel):
    name: str
    price: int


class OrderCreateSchema(BaseModel):
    items: list[ItemSchema]


class OrderReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Status
    items: list[ItemSchema]
    total_price: int
