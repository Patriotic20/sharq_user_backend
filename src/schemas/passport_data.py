from pydantic import BaseModel, ConfigDict , Field
from datetime import date
from typing import Optional




    
    
    
class PersonalInfo(BaseModel):
    photo: str
    jshshir: str = Field(alias="pinfl")
    passport_series_number: str = Field(alias="serialAndNumber")
    gender: str
    citizenship: str
    nationality: str
    date_of_birth: date = Field(alias="birthDate")
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    third_name: str = Field(alias="fatherName")
    issue_date: date = Field(alias="givenDate")
    passport_expire_date: date = Field(alias="passportExpireDate")
    country: str
    region: str
    district: str
    address: str
    

class PassportDataBase(BaseModel):
    passport_series_number: str
    jshshir: str


class PassportDataCreate(PersonalInfo):
    user_id: int
    passport_filepath: str


class PassportDataResponse(PassportDataBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PassportDataUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    third_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    passport_series_number: Optional[str] = None
    jshshir: Optional[str] = None
    issue_date: Optional[date] = None
    gender: Optional[str] = None
