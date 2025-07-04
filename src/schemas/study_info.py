from pydantic import BaseModel , ConfigDict
from .study_language import StudyLanguageResponse
from .study_form import StudyFormResponse
from .study_direction import StudyDirectionResponse

class StudyInfoBase(BaseModel):
    study_language_id: int
    study_form_id: int
    study_direction_id: int



class StudyInfoCreate(StudyInfoBase):
    user_id: int



class StudyInfoUpdate(BaseModel):
    study_language_id: int | None = None
    study_form_id: int | None = None
    study_direction_id: int | None = None



class StudyInfoFilter(BaseModel):
    study_language: int | None = None
    study_form: int | None = None
    study_direction: int | None = None



class StudyInfoResponse(BaseModel):
    id: int
    user_id: int
    study_language: StudyLanguageResponse
    study_form: StudyFormResponse
    study_direction: StudyDirectionResponse

    model_config = ConfigDict(from_attributes=True)



