from sqlmodel import Session, select
from app.database import engine
from app.models.models import User
from app.core import security

def create_first_user():
    email = "saeed@s3eed.ae"
    password = "admin123"
    
    with Session(engine) as session:
        # Check if user exists
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        
        if user:
            print(f"User {email} already exists.")
            return

        print(f"Creating superuser {email}...")
        
        hashed_password = security.get_password_hash(password)
        
        # Determine if 'role_id' is needed. Assuming superuser boolean is sufficient for now.
        # If roles are implemented, we would fetch or create an Admin role here.
        
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name="Saeed Admin",
            is_active=True,
            is_superuser=True
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        print(f"Superuser created successfully: {new_user.email}")

if __name__ == "__main__":
    create_first_user()
