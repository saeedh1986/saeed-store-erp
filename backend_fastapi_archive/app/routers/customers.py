from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Role
from app.schemas.customer import CustomerCreate, CustomerRead
import secrets

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.post("", response_model=CustomerRead)
def create_or_update_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Check if exists
    db_user = db.query(User).filter(User.email == customer.email).first()
    
    if db_user:
        # Update existing
        db_user.full_name = customer.full_name
        db.commit()
        db.refresh(db_user)
        return db_user
    
    # Create New
    # 1. Get or Create 'customer' role
    role = db.query(Role).filter(Role.name == "customer").first()
    if not role:
        role = Role(name="customer", description="Standard customer")
        db.add(role)
        db.commit()
        db.refresh(role)
        
    # 2. Create User
    # Generate random password as they won't login via password initially
    random_pass = secrets.token_urlsafe(16)
    
    db_user = User(
        email=customer.email,
        full_name=customer.full_name,
        hashed_password=random_pass, # In real app, hash this!
        role_id=role.id,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/by-email/{email}", response_model=CustomerRead)
def get_customer_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return user
