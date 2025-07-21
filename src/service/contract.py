import os
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.service import BasicCrud
from sharq_models.models import Contract  # type: ignore


class ReportService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_user_contract(self, user_id: int) -> Contract:
        contract_data = await super().get_by_field(
            model=Contract,
            field_name="user_id",
            field_value=user_id
        )

        if not contract_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User contract not found"
            )

        if not contract_data.status:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Contract not allowed"
            )

        return contract_data

    async def download_pdf(self, user_id: int) -> object:
        contract = await self.get_user_contract(user_id)
        file_path = contract.file_path

        if not file_path or not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return open(file_path, mode="rb")  # return file-like object for StreamingResponse
