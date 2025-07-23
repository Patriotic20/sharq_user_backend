from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sharq_models.models import Contract  # type: ignore
from src.service import BasicCrud
import os
import httpx


class ReportService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)

    async def download_pdf(self, user_id: int):
        contract = await super().get_by_field(
            model=Contract,
            field_name="user_id",
            field_value=user_id
        )

        if not contract or not contract.file_path:
            raise HTTPException(status_code=404, detail="Contract not found")

        file_url = contract.file_path
        filename = os.path.basename(file_url)

        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="File not found on remote server")

        return filename, response.content
