from pydantic import BaseModel, ConfigDict
from .study_language import StudyLanguageResponse
from .study_form import StudyFormResponse
from .study_direction import StudyDirectionResponse
from typing import Optional


class StudyInfoBase(BaseModel):
    study_language_id: int
    study_form_id: int
    study_direction_id: int


class StudyInfoCreate(StudyInfoBase):
    user_id: int


class StudyInfoUpdate(BaseModel):
    study_language_id: Optional[int] = None
    study_form_id: Optional[int] = None
    study_direction_id: Optional[int] = None


class StudyInfoFilter(BaseModel):
    study_language: Optional[int] = None
    study_form: Optional[int] = None
    study_direction: Optional[int] = None


class StudyInfoResponse(BaseModel):
    id: int
    user_id: int
    study_language: StudyLanguageResponse
    study_form: StudyFormResponse
    study_direction: StudyDirectionResponse

    model_config = ConfigDict(from_attributes=True)
