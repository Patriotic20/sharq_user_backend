from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sharq_models.models.user import Role #type: ignore
from src.schemas.role import RoleBase, RoleCreate, RoleResponse
from src.service import BasicCrud


class RoleService(BasicCrud[Role, RoleBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        existing_role = await self.get_by_field(
            model=Role, field_name="name", field_value=role_data.name
        )
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ushbu nom bilan rol allaqachon mavjud",
            )

        return await super().create(model=Role, obj_items=role_data)

    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        role = await super().get_by_id(model=Role, item_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol topilmadi"
            )
        return role

    async def get_default_role(self) -> Role:
        stmt = select(Role).where(Role.name == "user")
        result = await self.db.execute(stmt)
        role = result.scalars().first()

        if not role:
            default_role_data = RoleCreate(
                name="user", description="Default user role", permissions='["read:own"]'
            )
            role = await self.create_role(default_role_data)

        return role
