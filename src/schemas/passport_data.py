from pydantic import BaseModel , ConfigDict
from datetime import date


class PassportDataBase(BaseModel):
    first_name: str
    last_name: str
    third_name: str
    date_of_birth: date
    passport_series_number: str
    jshshir: str
    issue_date: date
    gender: str



class PassportDataCreate(PassportDataBase):
    user_id: int
    passport_filepath: str


class PassportDataResponse(PassportDataBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PassportDataUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    third_name: str | None = None
    date_of_birth: date | None = None
    passport_series_number: str | None = None
    jshshir: str | None = None
    issue_date: date | None = None
    gender: str | None = None
