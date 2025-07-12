from pydantic import BaseModel, ConfigDict
from .study_language import StudyLanguageResponse
from .study_form import StudyFormResponse
from .study_direction import StudyDirectionResponse


class StudyInfoBase(BaseModel):
    study_language_id: int
    study_form_id: int
    study_direction_id: int


class StudyInfoCreateRequest(StudyInfoBase):
    pass


class StudyInfoCreate(StudyInfoBase):
    user_id: int


class StudyInfoResponse(BaseModel):
    id: int
    user_id: int

    study_language: StudyLanguageResponse
    study_form: StudyFormResponse
    study_direction: StudyDirectionResponse

    model_config = ConfigDict(from_attributes=True)
