from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemBase(BaseModel):
    product_sku: str
    quantity: int
    unit_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemRead(OrderItemBase):
    id: int
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    external_id: str
    status: str
    total_amount: float
    currency: str = "AED"
    ai_risk_score: Optional[float] = None
    ai_notes: Optional[str] = None

class OrderCreate(BaseModel):
    wc_id: int # Mapped to external_id
    customer_email: str
    status: str
    total_amount: float
    currency: str
    items: List[OrderItemCreate]
    ai_risk_score: Optional[float] = None
    ai_notes: Optional[str] = None

class OrderRead(OrderBase):
    id: int
    customer_id: int
    created_at: datetime
    items: List[OrderItemRead]
    
    class Config:
        from_attributes = True
