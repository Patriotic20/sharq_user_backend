from pydantic import BaseModel , ConfigDict
from .passport_data import PassportDataResponse
from .study_info import StudyInfoResponse
from datetime import date

class ApplicationBase(BaseModel):
    study_info_id: int
    passport_data_id: int



class ApplicationResponse(ApplicationBase):
    id: int
    study_info: StudyInfoResponse
    passport_data : PassportDataResponse

    model_config = ConfigDict(from_attributes=True)



class ApplicationFilter(BaseModel):
    passport_series_number: str | None = None
    issue_date: date | None = None
    issuing_authority: str | None = None
    authority_code: str | None = None
    place_of_birth: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    nationality: str | None = None
    study_direction_name: str | None = None
    study_form_name: str | None = None
    study_language_name: str | None = None
