from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=True)
    description = Column(String, nullable=True)
    
    # Pricing
    price = Column(Float, default=0.0) # Selling Price
    cost_price = Column(Float, default=0.0) # Average Cost
    tax_rate = Column(Float, default=0.0) # e.g. 0.05 for 5% VAT
    
    # Organization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    
    # Media
    image_url = Column(String, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    stock_moves = relationship("StockMove", back_populates="product")

    @property
    def current_stock(self):
        # This will be calculated dynamically from stock moves in the service layer
        # But we can keep a cached field if performance demands it later
        return 0 

class StockMove(Base):
    """
    Double-Entry Inventory Ledger.
    Every change in stock is a 'Move'.
    """
    __tablename__ = "stock_moves"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    
    quantity = Column(Float) # Positive for IN, Negative for OUT
    type = Column(String) # 'purchase', 'sale', 'adjustment', 'return'
    reference = Column(String, nullable=True) # PO-123, SALE-456
    
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", back_populates="stock_moves")
