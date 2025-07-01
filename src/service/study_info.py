from fastapi import HTTPException , status
from src.service import BasicCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_info import StudyInfoCreate , StudyInfoBase , StudyInfoFilter
from src.models import StudyInfo

class StudyInfoCrud(BasicCrud[StudyInfo , StudyInfoBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_study_info(self, obj_info: StudyInfoBase , user_id: int):
        new_info = StudyInfoCreate(
            user_id=user_id,
            **obj_info.model_dump()
        )
        return await self._create_study_info_if_not_exists(obj=new_info)

    async def get_by_id_study_info(self , study_info_id: int , user_id: int):
        study_info = await super().get_by_id(model=StudyInfo, item_id=study_info_id)

        if not study_info:  
            raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

        if study_info.user_id != user_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")

        return study_info
    
    async def get_all_study_info(
        self,
        filters_data: StudyInfoFilter,
        limit: int = 100,
        offset: int = 0,
    ):
        filters = []

        if filters_data.study_language:
            filters.append(StudyInfo.study_language == filters_data.study_language)
        if filters_data.study_form:
            filters.append(StudyInfo.study_form == filters_data.study_form)
        if filters_data.study_direction:
            filters.append(StudyInfo.study_direction == filters_data.study_direction)
        if filters_data.exam_form:
            filters.append(StudyInfo.exam_form == filters_data.exam_form)

        return await super().get_all(
            model=StudyInfo,
            limit=limit,
            offset=offset,
            filters=filters or None
        )
    
    async def update_study_info(self, study_info_id: int, obj: StudyInfoBase , user_id: int):
        await self.get_by_id_study_info(study_info_id=study_info_id ,  user_id=user_id)
        return await super().update(model=StudyInfo, item_id=study_info_id, obj_items=obj)
    
    async def delete_study_info(self , study_info_id: int , user_id: int):
        await self.get_by_id_study_info(study_info_id=study_info_id ,  user_id=user_id)
        return await super().delete(model=StudyInfo , item_id=study_info_id)


    async def _create_study_info_if_not_exists(self, obj:StudyInfoCreate):
        exist_user = await super().get_by_field(
            model=StudyInfo, 
            field_name="user_id", 
            field_value=obj.user_id
            )
        if exist_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Foydalanuvchiga tegishli ma'lumot allaqachon mavjud"
            )       
        return await super().create(model=StudyInfo , obj_items=obj) 
