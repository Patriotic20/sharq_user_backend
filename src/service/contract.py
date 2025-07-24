from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sharq_models.models import Contract  # type: ignore
from src.service import BasicCrud
from urllib.parse import urljoin
from sqlalchemy import select
import os
import httpx


class ReportService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)
        self.BASE_FILE_SERVER_URL = "https://admin.sharqedu.uz"

    async def get_all_reports_by_id(self, user_id: int):
        stmt = select(Contract).where(Contract.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def _download_from_path(self, file_path: str) -> tuple[str, bytes]:
        file_url = urljoin(self.BASE_FILE_SERVER_URL + "/", file_path.lstrip("/"))
        filename = os.path.basename(file_path)

        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="File not found on remote server")

        return filename, response.content

    async def get_two_side_report(self, user_id: int) -> tuple[str, bytes] | None:
        contract_list = await self.get_all_reports_by_id(user_id)
        for contract in contract_list:
            if contract.file_path and "two_side" in contract.file_path:
                return await self._download_from_path(contract.file_path)
        return None

    async def get_three_side_report(self, user_id: int) -> tuple[str, bytes] | None:
        contract_list = await self.get_all_reports_by_id(user_id)
        for contract in contract_list:
            if contract.file_path and "three_side" in contract.file_path:
                return await self._download_from_path(contract.file_path)
        return None
