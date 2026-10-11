import httpx

from order_service.schemas import PaymentCreateSchema


class PaymentHTTPClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url)

    async def create_payment(self, data: PaymentCreateSchema):
        json_data = data.model_dump(mode="json")

        response = await self._client.post(
            "/payments",
            json=json_data,
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()
