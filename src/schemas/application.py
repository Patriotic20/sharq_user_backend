from pydantic import BaseModel, ConfigDict
from .passport_data import PassportDataResponse
from .study_info import StudyInfoResponse
from datetime import date
from typing import Optional


class ApplicationBase(BaseModel):
    study_info_id: int
    passport_data_id: int


class ApplicationResponse(ApplicationBase):
    id: int
    study_info: StudyInfoResponse
    passport_data: PassportDataResponse

    model_config = ConfigDict(from_attributes=True)


class ApplicationFilter(BaseModel):
    passport_series_number: Optional[str] = None
    issue_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    authority_code: Optional[str] = None
    place_of_birth: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    study_direction_name: Optional[str] = None
    study_form_name: Optional[str] = None
    study_language_name: Optional[str] = None
