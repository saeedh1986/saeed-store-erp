from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
# Update import to use the consolidated 'models' module
from app.models.models import Product, Category, StockMove
from app.schemas.inventory import ProductCreate, ProductRead, StockMoveCreate, StockMoveRead, CategoryCreate, CategoryRead

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

# --- Categories ---
@router.post("/categories", response_model=CategoryRead)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryRead])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# --- Products ---
@router.post("/products", response_model=ProductRead)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_data = product.dict()
    # Handle conversion: Price (float) -> Price Cents (int)
    price = product_data.pop("price", 0.0)
    price_cents = int(round(price * 100))
    
    db_product = Product(**product_data, price_cents=price_cents)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products", response_model=List[ProductRead])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    
    # Calculate stock for each product
    for p in products:
        stock_sum = db.query(func.sum(StockMove.quantity)).filter(StockMove.product_id == p.id).scalar()
        p.current_stock = stock_sum if stock_sum else 0.0
        
    return products

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock_sum = db.query(func.sum(StockMove.quantity)).filter(StockMove.product_id == product.id).scalar()
    product.current_stock = stock_sum if stock_sum else 0.0
    
    return product

# --- Stock Moves ---
@router.post("/moves", response_model=StockMoveRead)
def create_stock_move(move: StockMoveCreate, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(Product).filter(Product.id == move.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db_move = StockMove(**move.dict())
    db.add(db_move)
    db.commit()
    db.refresh(db_move)
    return db_move

@router.get("/moves/{product_id}", response_model=List[StockMoveRead])
def get_product_moves(product_id: int, db: Session = Depends(get_db)):
    return db.query(StockMove).filter(StockMove.product_id == product_id).order_by(StockMove.created_at.desc()).all()
