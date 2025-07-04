from pydantic import BaseModel , ConfigDict

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
    name: str | None = None
    study_form: str | None = None
    contract_sum: str | None = None
    education_years: str | None = None
    study_code: str | None = None

class StudyDirectionFilter(BaseModel):
    name: str | None = None
    study_form: str | None = None
    contract_sum: str | None = None
    education_years: str | None = None
    study_code: str | None = None
