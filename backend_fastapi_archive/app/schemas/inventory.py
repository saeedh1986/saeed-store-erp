from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    sku: str
    barcode: Optional[str] = None
    description: Optional[str] = None
    price: float = 0.0
    cost_price: float = 0.0
    tax_rate: float = 0.0
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    # Add other fields as needed

class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    current_stock: float = 0.0 # Computed field
    
    class Config:
        from_attributes = True

# Stock Move Schemas
class StockMoveBase(BaseModel):
    product_id: int
    quantity: float
    type: str # purchase, sale, adjustment
    reference: Optional[str] = None
    description: Optional[str] = None

class StockMoveCreate(StockMoveBase):
    pass

class StockMoveRead(StockMoveBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
