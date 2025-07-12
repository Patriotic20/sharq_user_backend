from src.clients import BaseClient
from src.core.config import settings


class PassportDataClient(BaseClient):
    def __init__(self):
        super().__init__(settings.passport_data_base_url)
        self.phone_number = settings.passport_data_username
        self.password = settings.passport_data_password
        self.token = None

    async def login(self):
        response = await self._make_request(
            method="POST",
            url=f"{self.base_url}/auth/sign-in",
            json={
                "phoneNumber": self.phone_number,
                "password": self.password,
            },
        )
        self.token = response.json().get("data", {}).get("token")
        return response

    async def get_passport_data(self, passport_series_number: str, jshshir: str):
        if not self.token:
            await self.login()

        headers = {"Authorization": f"Bearer {self.token}", **self.default_headers}

        response = await self._make_request(
            method="POST",
            url=f"{self.base_url}/user/personal-info",
            headers=headers,
            json={
                "serialAndNumber": passport_series_number,
                "pinfl": jshshir,
            },
        )
        return response
