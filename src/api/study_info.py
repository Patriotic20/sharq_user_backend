from fastapi import APIRouter, Depends , UploadFile , File
from src.service.study_info import StudyInfoCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_info import (
    StudyInfoCreate,
    StudyInfoResponse,
    StudyInfoCreateRequest,
)
from src.core.db import get_db
from sharq_models.models import User
from src.utils.auth import require_roles 
from src.utils.work_with_file import save_uploaded_file
from typing import Annotated

study_info_router = APIRouter(prefix="/study_info", tags=["Study Info"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyInfoCrud(db)


@study_info_router.post("/create")
async def create_user_study_info(
    study_language_id: int,
    study_form_id: int,
    study_direction_id: int,
    study_type_id: int,
    education_type_id: int,
    graduate_year: str,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
    certificate_path: UploadFile = File(None), 
    dtm_sheet: UploadFile = File(None),
    
    
):
    
    certificate_file_path = None
    dtm_sheet_file_path = None
    
    if certificate_path:
        certificate_file_path = await save_uploaded_file(certificate_path)
        
    if dtm_sheet:
        dtm_sheet_file_path = await save_uploaded_file(dtm_sheet)
        
        
    
    study_info = StudyInfoCreateRequest(
        study_language_id=study_language_id,
            study_form_id = study_form_id,
            study_direction_id = study_direction_id,
            study_type_id = study_type_id,
            education_type_id = education_type_id,
            graduate_year = graduate_year,
            certificate_path=certificate_file_path,
            dtm_sheet=dtm_sheet_file_path        
    )
    
    return await service.create_study_info(
        study_info=StudyInfoCreate(
            user_id=current_user.id, 
            **study_info.model_dump()
        )
    )


@study_info_router.get("/")
async def get_user_study_info(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> StudyInfoResponse:
    return await service.get_study_info_by_user_id(user_id=current_user.id)
