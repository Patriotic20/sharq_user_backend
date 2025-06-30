from pydantic import BaseModel
from datetime import  date

class PassportDataBase(BaseModel):
    passport_series_number: str
    issue_date: date
    issuing_authority: str
    authority_code: str
    place_of_birth: str
    date_of_birth: date
    gender: str
    nationality: str


class PassportDataCreate(PassportDataBase):
    user_id: int


class PassportDataResponse(PassportDataCreate):
    id: int


class PassportDataUpdate(BaseModel):
    passport_series_number: str | None = None
    issue_date: date | None = None
    issuing_authority: str | None = None
    authority_code: str | None = None
    place_of_birth: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    nationality: str | None = None
