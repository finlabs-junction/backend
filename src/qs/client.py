from __future__ import annotations

import typing as t 

import httpx
import msgspec

from qs.exceptions import ErrorMeta


T = t.TypeVar("T")


class Client:
    """
    Feature-less HTTP client.
    """
    def __init__(
        self, 
        base_url: str,
        auth: tuple[str, str] | None = None,
    ):
        self._base_url = f"{base_url}/api/v1"
        self._client = httpx.AsyncClient(
            base_url=self._base_url, 
            auth=auth,
        )


    def get_base_url(self) -> str:
        return self._base_url


    @staticmethod
    def raise_for_status(response: httpx.Response) -> None:
        if response.status_code >= 300:
            body = response.json()
            raise ErrorMeta.reconstruct(body)


    @t.overload
    async def request(
        self,
        method: str,
        path: str,
        type: type[T],
        *,
        body: t.Any = None,
        **params: t.Any,
    ) -> T:
        ...


    @t.overload
    async def request(
        self,
        method: str,
        path: str,
        *,
        body: t.Any = None,
        **params: t.Any,
    ) -> None:
        ...


    async def request(
        self,
        method: str,
        path: str,
        type: type[T] | None = None,
        *,
        body: t.Any = None,
        **params: t.Any,
    ) -> T | None:
        response = await self._client.request(
            method=method, 
            url=path, 
            params=params, 
            json=msgspec.to_builtins(body),
        )

        self.raise_for_status(response)

        if type is None:
            return
        
        body = response.read()
        return msgspec.json.decode(body, type=type)


    async def get(
        self, 
        path: str, 
        type: type[T],
        **params: t.Any,
    ) -> T:
        return await self.request("GET", path, type, **params)
    

    async def post(
        self,
        path: str,
        type: type[T] | None = None, 
        *,
        body: t.Any = None,
        **params: t.Any,
    ) -> T:
        if type is None:
            return await self.request("POST", path, body=body, **params)
        else:
            return await self.request("POST", path, type, body=body, **params)
    
    
    async def put(
        self,
        path: str,
        type: type[T] | None = None,
        *,
        body: t.Any = None,
        **params: t.Any,
    ) -> T:
        if type is None:
            return await self.request("PUT", path, body=body, **params)
        else:
            return await self.request("PUT", path, type, body=body, **params)
    

    async def patch(
        self,
        path: str,
        type: type[T] | None = None,
        *,
        body: t.Any = None,
        **params: t.Any,
    ) -> T:
        if type is None:
            return await self.request("PATCH", path, body=body, **params)
        else:
            return await self.request("PATCH", path, type, body=body, **params)
    

    async def delete(
        self,
        path: str,
        type: type[T] | None = None,
        **params: t.Any,
    ) -> T:
        if type is None:
            return await self.request("DELETE", path, **params)
        else:
            return await self.request("DELETE", path, type, **params)
