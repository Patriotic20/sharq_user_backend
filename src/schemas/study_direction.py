from pydantic import BaseModel, ConfigDict
from typing import Optional


class StudyDirectionBase(BaseModel):
    name: str
    study_form: str
    contract_sum: str
    education_years: str
    study_code: str


class StudyDirectionResponse(StudyDirectionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudyDirectionUpdate(BaseModel):
    name: Optional[str] = None
    study_form: Optional[str] = None
    contract_sum: Optional[str] = None
    education_years: Optional[str] = None
    study_code: Optional[str] = None


class StudyDirectionFilter(BaseModel):
    name: Optional[str] = None
    study_form: Optional[str] = None
    contract_sum: Optional[str] = None
    education_years: Optional[str] = None
    study_code: Optional[str] = None
