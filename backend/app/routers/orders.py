from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Order, OrderItem, Product, User, StockMove
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.post("", response_model=OrderRead)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # 1. Check Idempotency
    existing = db.query(Order).filter(Order.external_id == str(order_data.wc_id)).first()
    if existing:
         return existing

    # 2. Resolve Customer
    customer = db.query(User).filter(User.email == order_data.customer_email).first()
    if not customer:
        raise HTTPException(status_code=400, detail=f"Customer {order_data.customer_email} not found. Create customer first.")

    # 3. Create Order Header
    new_order = Order(
        external_id=str(order_data.wc_id),
        customer_id=customer.id,
        status=order_data.status,
        total_amount=order_data.total_amount,
        currency=order_data.currency,
        ai_risk_score=order_data.ai_risk_score,
        ai_notes=order_data.ai_notes
    )
    db.add(new_order)
    db.flush() # Generate ID

    # 4. Process Items & Inventory
    for item in order_data.items:
        # Find Product
        product = db.query(Product).filter(Product.sku == item.product_sku).first()
        
        if not product:
            # OPTIONAL: Auto-create product stub? For now, we skip to avoid crashing
            continue
            
        # Create Order Item
        db_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.quantity * item.unit_price
        )
        db.add(db_item)
        
        # INVENTORY HOOK: Deduct Stock
        stock_move = StockMove(
            product_id=product.id,
            quantity=-abs(item.quantity), # Negative for sale
            type="sale",
            reference=f"WC-ORDER-{order_data.wc_id}",
            description=f"Sold in Order #{order_data.wc_id}"
        )
        db.add(stock_move)

    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/by-wc-id/{wc_id}", response_model=OrderRead)
def get_order_by_wc_id(wc_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.external_id == wc_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
