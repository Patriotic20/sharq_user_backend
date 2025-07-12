import httpx


class BaseClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @property
    def default_headers(self):
        return {"Content-Type": "application/json", "Accept": "application/json"}

    async def _make_request(
        self, method: str, url: str, headers: dict = None, **kwargs
    ):
        if not headers:
            headers = self.default_headers

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            return response
