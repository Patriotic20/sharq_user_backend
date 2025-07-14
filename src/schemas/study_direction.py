from pydantic import BaseModel, ConfigDict
from .study_form import StudyFormResponse
from .study_type import StudyTypeResponse
from .study_language import StudyLanguageResponse
from .education_type import EducationTypeResponse
from typing import Optional


class StudyDirectionBase(BaseModel):
    name: str 
    exam_title: str 
    
    education_years: int
    contract_sum: float 
    study_code: str 
    
    study_form_id: int
    study_type_id: int
    study_language_id: int
    education_type_id: int


class StudyDirectionResponse(BaseModel):
    id: int
    name: str 
    exam_title: str 
    
    education_years: int
    contract_sum: float 
    study_code: str 
    
    
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



