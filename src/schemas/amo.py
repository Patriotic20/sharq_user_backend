from pydantic import BaseModel

class AMOCrmLead(BaseModel):
    user_id: int
    contact_id: int
    lead_id: int
    contact_data: dict
    lead_data: dict
    phone_number: str