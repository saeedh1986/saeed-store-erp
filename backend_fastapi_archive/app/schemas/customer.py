from pydantic import BaseModel, EmailStr
from typing import Optional

class CustomerBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerRead(CustomerBase):
    id: int
    role_id: Optional[int] = None
    
    class Config:
        from_attributes = True
