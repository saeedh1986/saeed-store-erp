
try:
    from backend.app.models.models import Role, User, Product
    from sqlmodel import SQLModel
    print("✅ Success: Models loaded correctly without SQLModel/Pydantic errors.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
