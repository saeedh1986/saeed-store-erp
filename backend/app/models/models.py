from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel, Relationship

# --- Role ---
class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    permissions: Optional[Dict] = Field(default=None, sa_column=Field(sa_type=JSON))
    
    users: List["User"] = Relationship(back_populates="role")

# --- User ---
class User(SQLModel, table=True):
    """Application user with role-based access control."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    role: Optional[Role] = Relationship(back_populates="users")

# --- Category ---
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    
    products: List["Product"] = Relationship(back_populates="category")

# --- Product ---
class Product(SQLModel, table=True):
    """Product catalog entry – master data for inventory and WooCommerce sync."""
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True, unique=True, nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    price_cents: int = Field(nullable=False, description="Price in smallest currency unit")
    currency: str = Field(default="AED", max_length=3)
    
    cost_price: float = Field(default=0.0)
    tax_rate: float = Field(default=0.0)
    image_url: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="products")
    
    stock_moves: List["StockMove"] = Relationship(back_populates="product")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def price(self) -> float:
        return self.price_cents / 100.0

# --- StockMove ---
class StockMove(SQLModel, table=True):
    """Double-Entry Inventory Ledger."""
    __tablename__ = "stock_moves"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: float = Field(description="Positive for IN, Negative for OUT")
    type: str = Field(description="purchase, sale, adjustment, return")
    reference: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    product: Optional[Product] = Relationship(back_populates="stock_moves")

# --- OrderItem ---
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)
    
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship()

# --- Order ---
class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(unique=True, index=True, description="WooCommerce Order ID")
    customer_id: int = Field(foreign_key="user.id")
    status: str = Field(default="pending")
    total_amount: float = Field(nullable=False)
    currency: str = Field(default="AED")
    
    ai_risk_score: Optional[float] = Field(default=None)
    ai_notes: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    items: List[OrderItem] = Relationship(back_populates="order")
    customer: "User" = Relationship()

# --- SyncLog ---
class SyncLog(SQLModel, table=True):
    """Log of every integration attempt (WooCommerce, Ollama, etc.)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    entity_type: str = Field(nullable=False, description="Order, Product, etc.")
    entity_id: Optional[int] = Field(default=None, description="Database ID of the entity")
    operation: str = Field(nullable=False, description="Create, Update, Delete")
    status: str = Field(nullable=False, description="Success or Fail")
    details: Optional[Dict] = Field(default=None, sa_column=Field(sa_type=JSON))

# --- SyncQueue ---
class SyncQueue(SQLModel, table=True):
    """Queue of failed integration payloads for retry."""
    id: Optional[int] = Field(default=None, primary_key=True)
    payload: Dict = Field(nullable=False, sa_column=Field(sa_type=JSON))
    retry_count: int = Field(default=0)
    next_retry_at: Optional[datetime] = Field(default=None)
