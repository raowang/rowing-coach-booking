import logging
from typing import Any, Optional

import httpx

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class DirectusClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def request(
        self,
        method: str,
        path: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_collection(self, collection: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return await self.request("GET", f"/items/{collection}", params=params)

    async def get_item(self, collection: str, id: str) -> dict[str, Any]:
        return await self.request("GET", f"/items/{collection}/{id}")

    async def create_item(self, collection: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self.request("POST", f"/items/{collection}", data={"data": data})

    async def update_item(self, collection: str, id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self.request("PATCH", f"/items/{collection}/{id}", data={"data": data})

    async def delete_item(self, collection: str, id: str) -> dict[str, Any]:
        return await self.request("DELETE", f"/items/{collection}/{id}")

    async def query(
        self,
        collection: str,
        filter: Optional[dict[str, Any]] = None,
        sort: Optional[list[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if filter:
            params["filter"] = filter
        if sort:
            params["sort"] = sort
        return await self.get_collection(collection, params=params)


_directus_client: Optional[DirectusClient] = None


def get_directus_client() -> DirectusClient:
    global _directus_client
    if _directus_client is None:
        _directus_client = DirectusClient(
            base_url=settings.directus_url,
            token=settings.directus_token
        )
    return _directus_client
