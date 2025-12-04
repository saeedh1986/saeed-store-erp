from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import engine
from app.models.base import Base
# Import models to register them with Base
from app.models import user, inventory
from app.routers import inventory as inventory_router

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(inventory_router.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Saeed Store ERP V2 API"}
